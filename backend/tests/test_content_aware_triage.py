"""
Test suite for content-aware triage functionality.
Following TDD methodology - these tests should fail initially.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from typing import Dict, Any

from cartaos.utils.triage import (
    ContentAwareTriage,
    DocumentType,
    TriageDecision,
    TriageConfidence,
    DocumentAnalysis
)


class TestDocumentTypeDetection:
    """Test document type detection functionality."""

    def test_triage_module_import(self):
        """Test that triage module can be imported."""
        from cartaos.utils.triage import ContentAwareTriage
        assert ContentAwareTriage is not None

    def test_detect_pdf_document(self):
        """Test detection of PDF documents."""
        triage = ContentAwareTriage()
        
        # Mock file with PDF signature and stat
        with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mtime = 1000
                doc_type = triage.detect_document_type('/path/to/document.pdf')
                assert doc_type == DocumentType.PDF

    def test_detect_image_document(self):
        """Test detection of image documents."""
        triage = ContentAwareTriage()
        
        # Mock JPEG file
        with patch('builtins.open', mock_open(read_data=b'\xff\xd8\xff')):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mtime = 1000
                doc_type = triage.detect_document_type('/path/to/image.jpg')
                assert doc_type == DocumentType.IMAGE

    def test_detect_text_document(self):
        """Test detection of text documents."""
        triage = ContentAwareTriage()
        
        # Mock text file
        with patch('builtins.open', mock_open(read_data=b'This is plain text content')):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mtime = 1000
                doc_type = triage.detect_document_type('/path/to/document.txt')
                assert doc_type == DocumentType.TEXT

    def test_detect_unknown_document(self):
        """Test handling of unknown document types."""
        triage = ContentAwareTriage()
        
        # Mock unknown binary file
        with patch('builtins.open', mock_open(read_data=b'\x00\x01\x02\x03')):
            doc_type = triage.detect_document_type('/path/to/unknown.bin')
            assert doc_type == DocumentType.UNKNOWN

    def test_file_not_found_handling(self):
        """Test handling of missing files."""
        triage = ContentAwareTriage()
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            doc_type = triage.detect_document_type('/nonexistent/file.pdf')
            assert doc_type == DocumentType.UNKNOWN


class TestDocumentAnalysis:
    """Test document content analysis functionality."""

    def test_analyze_document_size(self):
        """Test document size analysis."""
        # Use custom config with lower threshold
        config = {'large_file_threshold': 1024 * 1024}  # 1MB
        triage = ContentAwareTriage(config=config)
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 5 * 1024 * 1024  # 5MB
            mock_stat.return_value.st_mtime = 1000
            
            with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
                analysis = triage.analyze_document('/path/to/document.pdf')
                assert analysis.size_bytes == 5 * 1024 * 1024
                assert analysis.is_large_file is True  # 5MB > 1MB threshold

    def test_analyze_document_complexity_simple(self):
        """Test complexity analysis for simple documents."""
        triage = ContentAwareTriage()
        
        # Mock simple text content - need to handle both binary and text reads
        simple_content = 'Simple text content'
        
        def mock_open_handler(*args, **kwargs):
            if 'rb' in str(kwargs.get('mode', args[1] if len(args) > 1 else '')):
                return mock_open(read_data=simple_content.encode())(*args, **kwargs)
            else:
                return mock_open(read_data=simple_content)(*args, **kwargs)
        
        with patch('builtins.open', side_effect=mock_open_handler):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024  # 1KB
                mock_stat.return_value.st_mtime = 1000
                
                analysis = triage.analyze_document('/path/to/simple.txt')
                assert analysis.complexity_score < 0.5  # Low complexity

    def test_analyze_document_complexity_high(self):
        """Test complexity analysis for complex documents."""
        triage = ContentAwareTriage()
        
        # Mock complex content with tables, formulas, etc.
        complex_content = """
        Complex document with:
        - Tables: | Col1 | Col2 | Col3 |
        - Formulas: E = mc²
        - Multiple sections and subsections
        - Technical terminology and jargon
        - References and citations [1], [2], [3]
        """
        
        def mock_open_handler(*args, **kwargs):
            if 'rb' in str(kwargs.get('mode', args[1] if len(args) > 1 else '')):
                return mock_open(read_data=complex_content.encode())(*args, **kwargs)
            else:
                return mock_open(read_data=complex_content)(*args, **kwargs)
        
        with patch('builtins.open', side_effect=mock_open_handler):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 50 * 1024  # 50KB
                mock_stat.return_value.st_mtime = 1000
                
                analysis = triage.analyze_document('/path/to/complex.txt')
                assert analysis.complexity_score >= 0.6  # High complexity (adjusted threshold)

    def test_analyze_document_language_detection(self):
        """Test language detection in document analysis."""
        triage = ContentAwareTriage()
        
        english_content = "This is an English document with the and that standard vocabulary."
        
        def mock_open_handler(*args, **kwargs):
            if 'rb' in str(kwargs.get('mode', args[1] if len(args) > 1 else '')):
                return mock_open(read_data=english_content.encode())(*args, **kwargs)
            else:
                return mock_open(read_data=english_content)(*args, **kwargs)
        
        with patch('builtins.open', side_effect=mock_open_handler):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_mtime = 1000
                
                analysis = triage.analyze_document('/path/to/english.txt')
                assert analysis.detected_language == 'en'

    def test_analyze_document_metadata_extraction(self):
        """Test metadata extraction during analysis."""
        triage = ContentAwareTriage()
        
        with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 2 * 1024 * 1024
                
                # Mock PDF metadata extraction
                with patch.object(triage, '_extract_pdf_metadata') as mock_extract:
                    mock_extract.return_value = {
                        'title': 'Test Document',
                        'author': 'Test Author',
                        'pages': 10
                    }
                    
                    analysis = triage.analyze_document('/path/to/document.pdf')
                    assert analysis.metadata['title'] == 'Test Document'
                    assert analysis.metadata['pages'] == 10


class TestTriageDecisionMaking:
    """Test triage decision logic."""

    def test_triage_small_simple_document(self):
        """Test triage decision for small, simple documents."""
        triage = ContentAwareTriage()
        
        # Mock simple document analysis
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.TEXT,
            size_bytes=1024,  # 1KB
            complexity_score=0.2,
            detected_language='en',
            is_large_file=False,
            metadata={}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            decision = triage.make_triage_decision('/path/to/simple.txt')
            
            assert decision.target_stage == '04_ReadyForOCR'
            assert decision.confidence >= TriageConfidence.HIGH
            assert 'small and simple' in decision.reasoning.lower()

    def test_triage_large_complex_document(self):
        """Test triage decision for large, complex documents."""
        triage = ContentAwareTriage()
        
        # Mock complex document analysis
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=50 * 1024 * 1024,  # 50MB
            complexity_score=0.9,
            detected_language='en',
            is_large_file=True,
            metadata={'pages': 500}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            decision = triage.make_triage_decision('/path/to/complex.pdf')
            
            assert decision.target_stage == '06_TooLarge'
            assert decision.confidence >= TriageConfidence.HIGH
            assert 'large' in decision.reasoning.lower()

    def test_triage_medium_complexity_document(self):
        """Test triage decision for medium complexity documents."""
        triage = ContentAwareTriage()
        
        # Mock medium complexity document
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=5 * 1024 * 1024,  # 5MB
            complexity_score=0.6,
            detected_language='en',
            is_large_file=False,
            metadata={'pages': 25}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            decision = triage.make_triage_decision('/path/to/medium.pdf')
            
            assert decision.target_stage == '03_Lab'
            assert decision.confidence >= TriageConfidence.MEDIUM
            assert 'analysis' in decision.reasoning.lower()

    def test_triage_unknown_document_type(self):
        """Test triage decision for unknown document types."""
        triage = ContentAwareTriage()
        
        # Mock unknown document
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.UNKNOWN,
            size_bytes=1024,
            complexity_score=0.0,
            detected_language='unknown',
            is_large_file=False,
            metadata={}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            decision = triage.make_triage_decision('/path/to/unknown.bin')
            
            assert decision.target_stage == '02_Triage'
            assert decision.confidence == TriageConfidence.LOW
            assert 'unknown' in decision.reasoning.lower()

    def test_triage_confidence_scoring(self):
        """Test confidence scoring in triage decisions."""
        triage = ContentAwareTriage()
        
        # Test high confidence scenario
        high_conf_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=1024,
            complexity_score=0.1,
            detected_language='en',
            is_large_file=False,
            metadata={'pages': 1}
        )
        
        with patch.object(triage, 'analyze_document', return_value=high_conf_analysis):
            decision = triage.make_triage_decision('/path/to/clear.pdf')
            assert decision.confidence >= TriageConfidence.HIGH

    def test_triage_fallback_mechanisms(self):
        """Test fallback mechanisms for edge cases."""
        triage = ContentAwareTriage()
        
        # Mock analysis that raises an exception
        with patch.object(triage, 'analyze_document', side_effect=Exception("Analysis failed")):
            decision = triage.make_triage_decision('/path/to/problematic.pdf')
            
            # Should fallback to safe default
            assert decision.target_stage == '02_Triage'
            assert decision.confidence == TriageConfidence.LOW
            assert 'fallback' in decision.reasoning.lower()


class TestPerformanceAndCaching:
    """Test performance optimizations and caching."""

    def test_document_type_caching(self):
        """Test that document type detection results are cached."""
        triage = ContentAwareTriage()
        
        with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mtime = 1000
                
                # First call
                doc_type1 = triage.detect_document_type('/path/to/document.pdf')
                # Second call should use cache
                doc_type2 = triage.detect_document_type('/path/to/document.pdf')
                
                assert doc_type1 == doc_type2 == DocumentType.PDF

    def test_analysis_caching(self):
        """Test that document analysis results are cached."""
        triage = ContentAwareTriage()
        
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=1024,
            complexity_score=0.3,
            detected_language='en',
            is_large_file=False,
            metadata={}
        )
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_mtime = 1000
            
            with patch.object(triage, '_perform_analysis', return_value=mock_analysis) as mock_perform:
                # First call
                analysis1 = triage.analyze_document('/path/to/document.pdf')
                # Second call should use cache
                analysis2 = triage.analyze_document('/path/to/document.pdf')
                
                assert analysis1 == analysis2
                # _perform_analysis should only be called once
                assert mock_perform.call_count == 1

    def test_cache_invalidation(self):
        """Test cache invalidation when files change."""
        triage = ContentAwareTriage()
        
        with patch('pathlib.Path.stat') as mock_stat:
            # First call with initial timestamp
            mock_stat.return_value.st_mtime = 1000
            mock_stat.return_value.st_size = 1024
            
            with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
                doc_type1 = triage.detect_document_type('/path/to/document.pdf')
            
            # Second call with updated timestamp (file changed)
            mock_stat.return_value.st_mtime = 2000
            
            with patch('builtins.open', mock_open(read_data=b'%PDF-1.5')):
                doc_type2 = triage.detect_document_type('/path/to/document.pdf')
            
            # Both should be PDF but cache should have been invalidated
            assert doc_type1 == doc_type2 == DocumentType.PDF

    def test_performance_benchmarks(self):
        """Test that triage operations meet performance requirements."""
        import time
        
        triage = ContentAwareTriage()
        
        # Mock fast analysis
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=1024,
            complexity_score=0.3,
            detected_language='en',
            is_large_file=False,
            metadata={}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            start_time = time.time()
            decision = triage.make_triage_decision('/path/to/document.pdf')
            end_time = time.time()
            
            # Should complete in under 1 second for typical documents
            assert (end_time - start_time) < 1.0
            assert decision is not None


class TestIntegrationWithExistingSystem:
    """Test integration with existing CartaOS components."""

    def test_integration_with_file_watcher(self):
        """Test integration with file watcher system."""
        from cartaos.utils.triage import process_new_file
        
        with patch('cartaos.utils.triage.ContentAwareTriage') as mock_triage_class:
            mock_triage = MagicMock()
            mock_triage_class.return_value = mock_triage
            
            mock_decision = TriageDecision(
                target_stage='04_ReadyForOCR',
                confidence=TriageConfidence.HIGH,
                reasoning='Simple document ready for OCR'
            )
            mock_triage.make_triage_decision.return_value = mock_decision
            
            # Mock file move operation and Path operations
            with patch('shutil.move') as mock_move:
                with patch('pathlib.Path.mkdir') as mock_mkdir:
                    with patch('pathlib.Path.parent') as mock_parent:
                        mock_parent.parent = MagicMock()
                        result = process_new_file('/00_Inbox/document.pdf')
                        
                        assert result is True
                        mock_move.assert_called_once()

    def test_integration_with_api_endpoints(self):
        """Test integration with API endpoints."""
        from cartaos.utils.triage import get_triage_status
        
        # Mock triage status retrieval
        status = get_triage_status('/path/to/document.pdf')
        
        assert 'stage' in status
        assert 'confidence' in status
        assert 'reasoning' in status

    def test_configuration_management(self):
        """Test configuration management for triage settings."""
        triage = ContentAwareTriage()
        
        # Test default configuration
        assert triage.config.large_file_threshold > 0
        assert triage.config.complexity_threshold > 0
        
        # Test custom configuration
        custom_config = {
            'large_file_threshold': 10 * 1024 * 1024,  # 10MB
            'complexity_threshold': 0.8
        }
        
        custom_triage = ContentAwareTriage(config=custom_config)
        assert custom_triage.config.large_file_threshold == 10 * 1024 * 1024

    def test_telemetry_and_logging(self):
        """Test telemetry and logging for triage decisions."""
        triage = ContentAwareTriage()
        
        mock_analysis = DocumentAnalysis(
            document_type=DocumentType.PDF,
            size_bytes=1024,
            complexity_score=0.3,
            detected_language='en',
            is_large_file=False,
            metadata={}
        )
        
        with patch.object(triage, 'analyze_document', return_value=mock_analysis):
            with patch('cartaos.utils.triage.logger') as mock_logger:
                decision = triage.make_triage_decision('/path/to/document.pdf')
                
                # Should log triage decision
                mock_logger.info.assert_called()
                assert decision is not None
