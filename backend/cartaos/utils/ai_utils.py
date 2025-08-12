# -*- coding: utf-8 -*-
# backend/cartaos/utils/ai_utils.py

"""
Utilities for interacting with the Gemini AI API.

This module provides functions for generating analytical summaries using the Gemini AI API.
"""

import os
import logging
from dotenv import load_dotenv
from google.genai import Client, models
from pathlib import Path
from typing import Optional

from cartaos import config

_CLIENT: Optional[Client] = None

def get_client() -> Client:
    """
    Creates and returns a singleton instance of the Gemini AI client.

    The client is created only once, and subsequent calls return the same instance.
    """
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    dotenv_path = config.BACKEND_DIR / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY not found in %s", dotenv_path)
        raise ValueError("API key is not configured.")

    _CLIENT = Client(api_key=api_key)
    logging.info("Gemini AI client initialized successfully.")
    return _CLIENT

def generate_summary(text: str) -> Optional[str]:
    """
    Generates the analytical summary using the Gemini AI API.

    Args:
        text (str): The text to be summarized.

    Returns:
        Optional[str]: Generated summary or None if generation fails.
    """
    try:
        client = get_client()
    except ValueError as e:
        logging.error("Failed to generate summary due to configuration error: %s", e)
        return None

    logging.info("Generating summary with AI model...")
    prompt_path = config.PROMPTS_DIR / 'summary_prompt.md'

    try:
        if not prompt_path.exists():
            logging.error("Prompt file not found at: %s", prompt_path)
            return None

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        prompt = prompt_template.format(text=text)

        response = client.models.generate_content(
            model='models/gemini-2.5-pro',
            contents=prompt
        )

        if response and hasattr(response, 'text'):
            logging.info("Summary generated successfully.")
            return response.text
        else:
            logging.warning("AI response was empty or did not contain text. Details: %s", response)
            return None

    except Exception as e:
        logging.error("Error during Gemini AI API call: %s", e, exc_info=True)
        return None
