"""
Application configuration for CartaOS.
"""
import os
from pathlib import Path
from typing import Dict, Optional


class AppConfig:
    """Application configuration class.
    
    This class holds all the configuration settings for the CartaOS application.
    It loads settings from environment variables with sensible defaults.
    """
    
    def __init__(self):
        """Initialize the application configuration.
        
        Raises:
            PermissionError: If directory creation fails
            OSError: For other filesystem errors
        """
        # API Keys
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        
        # Paths
        self.root_dir: Path = Path(__file__).parent.parent
        self.obsidian_vault_path: Path = Path(
            os.getenv("OBSIDIAN_VAULT_PATH", self.root_dir / "vault")
        )
        
        # Pipeline directories
        self.pipeline_dirs = {
            "00_Inbox": self.root_dir / "00_Inbox",
            "02_Triage": self.root_dir / "02_Triage",
            "03_Lab": self.root_dir / "03_Lab",
            "04_ReadyForOCR": self.root_dir / "04_ReadyForOCR",
            "05_ReadyForSummary": self.root_dir / "05_ReadyForSummary",
            "06_TooLarge": self.root_dir / "06_TooLarge",
            "07_Processed": self.root_dir / "07_Processed",
        }
        
        # Create directories if they don't exist
        for stage, dir_path in self.pipeline_dirs.items():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                if not os.access(dir_path, os.W_OK):
                    raise PermissionError(f"No write permissions for directory: {dir_path}")
            except PermissionError as pe:
                raise
            except Exception as e:
                raise OSError(f"Failed to create directory {stage}: {str(e)}") from e
    
    def get_pipeline_dir(self, stage: str) -> Path:
        """Get the path for a pipeline stage.
        
        Args:
            stage: The pipeline stage (e.g., "00_Inbox", "02_Triage", etc.)
            
        Returns:
            Path: The full path to the pipeline stage directory
            
        Raises:
            ValueError: If the stage is not found in the pipeline directories
        """
        if stage not in self.pipeline_dirs:
            raise ValueError(f"Unknown pipeline stage: {stage}")
        return self.pipeline_dirs[stage]


def get_config() -> AppConfig:
    '''
    Get the application configuration.
    
    This function is used to provide a singleton instance of the AppConfig class.
    It ensures that the configuration is loaded only once and the same instance
    is reused throughout the application.
    
    Returns:
        AppConfig: The application configuration instance
    '''
    if not hasattr(get_config, "_instance"):
        get_config._instance = AppConfig()
    return get_config._instance
