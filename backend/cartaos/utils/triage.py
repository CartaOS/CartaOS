"""
Content-aware triage system for intelligent document categorization.
Provides advanced document analysis and routing based on content, size, and complexity.
"""
import logging
import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, Union
import shutil
import re

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Document type classifications."""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    UNKNOWN = "unknown"


class TriageConfidence(Enum):
    """Confidence levels for triage decisions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@dataclass
class DocumentAnalysis:
    """Results of document content analysis."""
    document_type: DocumentType
    size_bytes: int
    complexity_score: float  # 0.0 to 1.0
    detected_language: str
    is_large_file: bool
    metadata: Dict[str, Any]


@dataclass
class TriageDecision:
    """Triage decision with reasoning."""
    target_stage: str
    confidence: TriageConfidence
    reasoning: str


@dataclass
class TriageConfig:
    """Configuration for triage system."""
    large_file_threshold: int = 10 * 1024 * 1024  # 10MB
    complexity_threshold: float = 0.7
    cache_ttl: int = 3600  # 1 hour
    enable_caching: bool = True


class ContentAwareTriage:
    """Content-aware triage system for intelligent document routing."""
    
    def __init__(self, config: Optional[Union[Dict[str, Any], TriageConfig]] = None):
        """Initialize triage system with configuration."""
        if config is None:
            self.config = TriageConfig()
        elif isinstance(config, dict):
            self.config = TriageConfig(**config)
        else:
            self.config = config
            
        self._type_cache: Dict[str, tuple] = {}  # (result, timestamp, file_mtime)
        self._analysis_cache: Dict[str, tuple] = {}  # (result, timestamp, file_mtime)
    
    def detect_document_type(self, file_path: str) -> DocumentType:
        """
        Detect document type based on file signature and extension.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            DocumentType: Detected document type
        """
        path = Path(file_path)
        
        # Check cache first
        if self.config.enable_caching and file_path in self._type_cache:
            cached_result, cache_time, cached_mtime = self._type_cache[file_path]
            
            try:
                current_mtime = path.stat().st_mtime
                if (time.time() - cache_time < self.config.cache_ttl and 
                    current_mtime == cached_mtime):
                    return cached_result
            except (OSError, FileNotFoundError):
                pass
        
        try:
            # Read file signature
            with open(file_path, 'rb') as f:
                signature = f.read(16)
            
            file_mtime = path.stat().st_mtime
            
            # Detect by file signature
            doc_type = self._detect_by_signature(signature, path.suffix.lower())
            
            # Cache result
            if self.config.enable_caching:
                self._type_cache[file_path] = (doc_type, time.time(), file_mtime)
            
            return doc_type
            
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return DocumentType.UNKNOWN
    
    def _detect_by_signature(self, signature: bytes, extension: str) -> DocumentType:
        """Detect document type by file signature and extension."""
        # PDF signature
        if signature.startswith(b'%PDF'):
            return DocumentType.PDF
        
        # Image signatures
        if (signature.startswith(b'\xff\xd8\xff') or  # JPEG
            signature.startswith(b'\x89PNG') or       # PNG
            signature.startswith(b'GIF8') or          # GIF
            signature.startswith(b'BM') or            # BMP
            signature.startswith(b'RIFF')):           # WebP/other RIFF
            return DocumentType.IMAGE
        
        # Office documents (ZIP-based)
        if signature.startswith(b'PK\x03\x04'):
            if extension in ['.xlsx', '.xls', '.ods']:
                return DocumentType.SPREADSHEET
            elif extension in ['.pptx', '.ppt', '.odp']:
                return DocumentType.PRESENTATION
            elif extension in ['.docx', '.doc', '.odt']:
                return DocumentType.TEXT
        
        # Plain text files
        if extension in ['.txt', '.md', '.csv', '.log']:
            return DocumentType.TEXT
        
        # Try to detect if it's text by checking for printable characters
        try:
            text_content = signature.decode('utf-8', errors='ignore')
            if all(c.isprintable() or c.isspace() for c in text_content):
                return DocumentType.TEXT
        except:
            pass
        
        return DocumentType.UNKNOWN
    
    def analyze_document(self, file_path: str) -> DocumentAnalysis:
        """
        Perform comprehensive document analysis.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            DocumentAnalysis: Analysis results
        """
        path = Path(file_path)
        
        # Check cache first
        if self.config.enable_caching and file_path in self._analysis_cache:
            cached_result, cache_time, cached_mtime = self._analysis_cache[file_path]
            
            try:
                current_mtime = path.stat().st_mtime
                if (time.time() - cache_time < self.config.cache_ttl and 
                    current_mtime == cached_mtime):
                    return cached_result
            except (OSError, FileNotFoundError):
                pass
        
        try:
            analysis = self._perform_analysis(file_path)
            
            # Cache result
            if self.config.enable_caching:
                file_mtime = path.stat().st_mtime
                self._analysis_cache[file_path] = (analysis, time.time(), file_mtime)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document {file_path}: {e}")
            # Return minimal analysis on error
            return DocumentAnalysis(
                document_type=DocumentType.UNKNOWN,
                size_bytes=0,
                complexity_score=0.0,
                detected_language='unknown',
                is_large_file=False,
                metadata={}
            )
    
    def _perform_analysis(self, file_path: str) -> DocumentAnalysis:
        """Perform the actual document analysis."""
        path = Path(file_path)
        
        # Get basic file info
        stat_info = path.stat()
        size_bytes = stat_info.st_size
        is_large_file = size_bytes > self.config.large_file_threshold
        
        # Detect document type
        doc_type = self.detect_document_type(file_path)
        
        # Analyze complexity
        complexity_score = self._calculate_complexity(file_path, doc_type)
        
        # Detect language
        detected_language = self._detect_language(file_path, doc_type)
        
        # Extract metadata
        metadata = self._extract_metadata(file_path, doc_type)
        
        return DocumentAnalysis(
            document_type=doc_type,
            size_bytes=size_bytes,
            complexity_score=complexity_score,
            detected_language=detected_language,
            is_large_file=is_large_file,
            metadata=metadata
        )
    
    def _calculate_complexity(self, file_path: str, doc_type: DocumentType) -> float:
        """Calculate document complexity score (0.0 to 1.0)."""
        try:
            if doc_type == DocumentType.TEXT:
                return self._analyze_text_complexity(file_path)
            elif doc_type == DocumentType.PDF:
                return self._analyze_pdf_complexity(file_path)
            elif doc_type == DocumentType.IMAGE:
                return self._analyze_image_complexity(file_path)
            else:
                return 0.5  # Default medium complexity for unknown types
        except Exception as e:
            logger.warning(f"Error calculating complexity for {file_path}: {e}")
            return 0.0
    
    def _analyze_text_complexity(self, file_path: str) -> float:
        """Analyze text document complexity."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # Read first 10KB for analysis
            
            complexity_indicators = 0
            
            # Check for tables (pipe characters in patterns)
            if re.search(r'\|.*\|.*\|', content):
                complexity_indicators += 1
            
            # Check for formulas/equations
            if re.search(r'[=∑∫∂√π]|E\s*=\s*mc²', content):
                complexity_indicators += 1
            
            # Check for technical terms (words with numbers/symbols)
            technical_terms = len(re.findall(r'\b\w*\d+\w*\b|\b\w*[α-ωΑ-Ω]\w*\b', content))
            if technical_terms > 10:
                complexity_indicators += 1
            
            # Check for citations/references
            if re.search(r'\[\d+\]|\(\d{4}\)|doi:|ISBN:', content):
                complexity_indicators += 1
            
            # Check for multiple sections/headers
            headers = len(re.findall(r'^#+\s|\n[A-Z][A-Z\s]+\n|^\d+\.\s', content, re.MULTILINE))
            if headers > 5:
                complexity_indicators += 1
            
            # Normalize to 0-1 scale
            return min(complexity_indicators / 5.0, 1.0)
            
        except Exception:
            return 0.0
    
    def _analyze_pdf_complexity(self, file_path: str) -> float:
        """Analyze PDF document complexity (simplified)."""
        # For now, use file size as a proxy for complexity
        # In a real implementation, you'd use PyPDF2 or similar
        try:
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            if size_mb < 1:
                return 0.2
            elif size_mb < 5:
                return 0.5
            elif size_mb < 20:
                return 0.8
            else:
                return 1.0
        except Exception:
            return 0.5
    
    def _analyze_image_complexity(self, file_path: str) -> float:
        """Analyze image document complexity."""
        # For images, complexity could be based on size and potential text content
        try:
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            # Larger images might contain more text/complex content
            return min(size_mb / 10.0, 1.0)
        except Exception:
            return 0.3
    
    def _detect_language(self, file_path: str, doc_type: DocumentType) -> str:
        """Detect document language (simplified implementation)."""
        if doc_type == DocumentType.TEXT:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # Read first 1KB
                
                # Simple heuristic: check for common English words
                english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
                word_count = sum(1 for word in english_words if word in content.lower())
                
                if word_count >= 3:
                    return 'en'
                else:
                    return 'unknown'
            except Exception:
                return 'unknown'
        else:
            return 'unknown'  # Language detection for non-text files would need OCR
    
    def _extract_metadata(self, file_path: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Extract document metadata."""
        metadata = {}
        
        try:
            if doc_type == DocumentType.PDF:
                metadata = self._extract_pdf_metadata(file_path)
            elif doc_type == DocumentType.IMAGE:
                metadata = self._extract_image_metadata(file_path)
            elif doc_type == DocumentType.TEXT:
                metadata = self._extract_text_metadata(file_path)
        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path}: {e}")
        
        return metadata
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata (simplified)."""
        # In a real implementation, use PyPDF2 or similar
        return {
            'title': Path(file_path).stem,
            'pages': 1,  # Placeholder
            'author': 'unknown'
        }
    
    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata."""
        path = Path(file_path)
        return {
            'format': path.suffix.lower().lstrip('.'),
            'filename': path.name
        }
    
    def _extract_text_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract text file metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            return {
                'line_count': len(lines),
                'char_count': sum(len(line) for line in lines)
            }
        except Exception:
            return {}
    
    def make_triage_decision(self, file_path: str) -> TriageDecision:
        """
        Make intelligent triage decision based on document analysis.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            TriageDecision: Triage decision with reasoning
        """
        try:
            analysis = self.analyze_document(file_path)
            
            # Log the triage decision
            logger.info(f"Making triage decision for {file_path}: "
                       f"type={analysis.document_type.value}, "
                       f"size={analysis.size_bytes}, "
                       f"complexity={analysis.complexity_score:.2f}")
            
            # Decision logic
            if analysis.document_type == DocumentType.UNKNOWN:
                return TriageDecision(
                    target_stage='02_Triage',
                    confidence=TriageConfidence.LOW,
                    reasoning='Unknown document type requires human review'
                )
            
            if analysis.is_large_file:
                return TriageDecision(
                    target_stage='06_TooLarge',
                    confidence=TriageConfidence.HIGH,
                    reasoning=f'Large file ({analysis.size_bytes / (1024*1024):.1f}MB) exceeds processing threshold'
                )
            
            if analysis.complexity_score > self.config.complexity_threshold:
                return TriageDecision(
                    target_stage='03_Lab',
                    confidence=TriageConfidence.HIGH,
                    reasoning=f'Complex document (score: {analysis.complexity_score:.2f}) needs detailed analysis'
                )
            
            if (analysis.complexity_score < 0.3 and 
                analysis.size_bytes < 1024 * 1024 and  # < 1MB
                analysis.document_type in [DocumentType.PDF, DocumentType.IMAGE, DocumentType.TEXT]):
                return TriageDecision(
                    target_stage='04_ReadyForOCR',
                    confidence=TriageConfidence.HIGH,
                    reasoning='Small and simple document ready for OCR processing'
                )
            
            # Default to lab for medium complexity
            return TriageDecision(
                target_stage='03_Lab',
                confidence=TriageConfidence.MEDIUM,
                reasoning=f'Medium complexity document requires analysis (score: {analysis.complexity_score:.2f})'
            )
            
        except Exception as e:
            logger.error(f"Error making triage decision for {file_path}: {e}")
            return TriageDecision(
                target_stage='02_Triage',
                confidence=TriageConfidence.LOW,
                reasoning='Fallback to human triage due to analysis error'
            )


# Global triage instance
_triage_instance: Optional[ContentAwareTriage] = None


def get_triage_instance() -> ContentAwareTriage:
    """Get or create global triage instance."""
    global _triage_instance
    if _triage_instance is None:
        _triage_instance = ContentAwareTriage()
    return _triage_instance


def process_new_file(file_path: str) -> bool:
    """
    Process a new file through the triage system.
    
    Args:
        file_path (str): Path to the file to process
        
    Returns:
        bool: True if processing succeeded
    """
    try:
        triage = get_triage_instance()
        decision = triage.make_triage_decision(file_path)
        
        # Move file to target stage
        source_path = Path(file_path)
        target_dir = source_path.parent.parent / decision.target_stage
        target_path = target_dir / source_path.name
        
        # Ensure target directory exists
        target_dir.mkdir(exist_ok=True)
        
        # Move the file
        shutil.move(str(source_path), str(target_path))
        
        logger.info(f"Moved {file_path} to {decision.target_stage} "
                   f"(confidence: {decision.confidence.value})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return False


def get_triage_status(file_path: str) -> Dict[str, Any]:
    """
    Get triage status for a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Dict[str, Any]: Triage status information
    """
    try:
        triage = get_triage_instance()
        decision = triage.make_triage_decision(file_path)
        
        return {
            'stage': decision.target_stage,
            'confidence': decision.confidence.value,
            'reasoning': decision.reasoning
        }
        
    except Exception as e:
        logger.error(f"Error getting triage status for {file_path}: {e}")
        return {
            'stage': '02_Triage',
            'confidence': 'low',
            'reasoning': f'Error during analysis: {str(e)}'
        }
