# -*- coding: utf-8 -*-
# backend/cartaos/config.py

import os
from pathlib import Path
from typing import Dict, Literal, Optional, TypedDict

from dotenv import load_dotenv

# Define the ROOT_DIR as the project's main folder (cartaos-cartaos)
# This path is calculated by going up 3 levels from config.py (config.py -> cartaos -> backend -> ROOT)
ROOT_DIR: Path = Path(__file__).parent.parent.parent

# Define the backend directory for convenience
BACKEND_DIR: Path = ROOT_DIR / "backend"

# Define the main package directory
CARTAOS_DIR: Path = BACKEND_DIR / "cartaos"

# Now, define all other important paths based on these bases
PROMPTS_DIR: Path = CARTAOS_DIR / "prompts"

# Pipeline directories
PIPELINE_STAGES: list[str] = [
    "00_Inbox",
    "02_Triage",
    "03_Lab",
    "04_ReadyForOCR",
    "05_ReadyForSummary",
    "06_TooLarge",
    "07_Processed",
]


class PipelineDirs:
    def __init__(self):
        self.pipeline_dirs = {
            "00_Inbox": ROOT_DIR / "00_Inbox",
            "02_Triage": ROOT_DIR / "02_Triage",
            "03_Lab": ROOT_DIR / "03_Lab",
            "04_ReadyForOCR": ROOT_DIR / "04_ReadyForOCR",
            "05_ReadyForSummary": ROOT_DIR / "05_ReadyForSummary",
            "06_TooLarge": ROOT_DIR / "06_TooLarge",
            "07_Processed": ROOT_DIR / "07_Processed",
        }


PIPELINE_DIRS = PipelineDirs()

# Example of how to access a specific directory:
# PIPELINE_DIRS["03_Lab"]


class AppConfig:
    """
    Application configuration class that loads all environment variables and settings.

    This class is responsible for loading configuration from .env files and environment
    variables. It should be instantiated once at the application's entry point and
    injected into components that need configuration.
    """

    def __init__(self, env_path: Optional[Path] = None) -> None:
        """
        Initialize the configuration by loading from .env file and environment variables.

        Args:
            env_path (Optional[Path]): Custom path to .env file. If None, uses default location.
        """
        # Load environment variables from .env file
        if env_path is None:
            env_path = BACKEND_DIR / ".env"

        load_dotenv(dotenv_path=env_path)

        # Load API configuration
        self.api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.obsidian_vault_path: Optional[str] = os.getenv("OBSIDIAN_VAULT_PATH")

        # Set up directory paths
        self.processed_pdf_dir: Path = ROOT_DIR / "07_Processed"

        # Initialize with default; override if OBSIDIAN_VAULT_PATH is set
        self.summary_dir: Path = self.processed_pdf_dir / "Summaries"
        if self.obsidian_vault_path and Path(self.obsidian_vault_path).is_dir():
            self.summary_dir = Path(self.obsidian_vault_path) / "Summaries"
