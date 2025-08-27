# -*- coding: utf-8 -*-
# backend/cartaos/config.py

import os
import pathlib
from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the ROOT_DIR as the project's main folder (cartaos-cartaos)
# This path is calculated by going up 3 levels from config.py (config.py -> cartaos -> backend -> ROOT)
ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent

# Define the backend directory for convenience
BACKEND_DIR: pathlib.Path = ROOT_DIR / "backend"

# Define the main package directory
CARTAOS_DIR: pathlib.Path = BACKEND_DIR / "cartaos"

# Now, define all other important paths based on these bases
PROMPTS_DIR: pathlib.Path = CARTAOS_DIR / "prompts"

# Pipeline directories
PIPELINE_STAGES: List[str] = [
    "00_Inbox",
    "02_Triage",
    "03_Lab",
    "04_ReadyForOCR",
    "05_ReadyForSummary",
    "06_TooLarge",
    "07_Processed",
]


class PipelineDirs:
    """Manages pipeline directories."""
    
    def __init__(self, base_dir: Optional[pathlib.Path] = None):
        """Initialize with optional base directory."""
        self.base_dir = base_dir or ROOT_DIR
        self.pipeline_dirs = {
            "00_Inbox": self.base_dir / "00_Inbox",
            "02_Triage": self.base_dir / "02_Triage",
            "03_Lab": self.base_dir / "03_Lab",
            "04_ReadyForOCR": self.base_dir / "04_ReadyForOCR",
            "05_ReadyForSummary": self.base_dir / "05_ReadyForSummary",
            "06_TooLarge": self.base_dir / "06_TooLarge",
            "07_Processed": self.base_dir / "07_Processed",
        }
    
    def __getitem__(self, key: str) -> pathlib.Path:
        """Get directory path by stage name."""
        return self.pipeline_dirs[key]
    
    def values(self):
        """Get all directory paths."""
        return self.pipeline_dirs.values()
    
    def items(self):
        """Get all stage name and directory path pairs."""
        return self.pipeline_dirs.items()


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    log_file: Optional[pathlib.Path] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External services
    gemini_api_key: str = ""
    obsidian_vault_path: pathlib.Path = ROOT_DIR / "vault"
    
    # File paths
    pipeline_dirs: Dict[str, pathlib.Path] = Field(default_factory=dict)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator('pipeline_dirs', mode='before')
    @classmethod
    def set_pipeline_dirs(cls, v):
        """Set default pipeline directories if not provided."""
        if not v:
            pipeline_dirs = PipelineDirs()
            return pipeline_dirs.pipeline_dirs
        return v


# Global settings instance
settings = Settings()

# Backward compatibility
PIPELINE_DIRS = PipelineDirs()
