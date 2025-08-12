# -*- coding: utf-8 -*-
# backend/cartaos/config.py

import pathlib
from typing import Dict, Literal, TypedDict

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
PIPELINE_STAGES: list[str] = ["00_Inbox", "02_Triage", "03_Lab", "04_ReadyForOCR", "05_ReadyForSummary", "06_TooLarge", "07_Processed"]

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

