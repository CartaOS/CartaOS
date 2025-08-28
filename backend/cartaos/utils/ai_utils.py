# -*- coding: utf-8 -*-
# backend/cartaos/utils/ai_utils.py

"""
Utilities for interacting with the Gemini AI API.

This module provides functions for generating analytical summaries using the Gemini AI API.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from google.genai import Client, models

from cartaos import get_config, config
from cartaos.config import settings
from .external_calls import ExternalCallManager

# Initialize logger
logger = logging.getLogger(__name__)

_CLIENT: Optional[Client] = None
_EXTERNAL_CALL_MANAGER: Optional[ExternalCallManager] = None


def get_client() -> Client:
    """
    Creates and returns a singleton instance of the Gemini AI client.

    The client is created only once, and subsequent calls return the same instance.
    """
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    # Get API key from AppConfig
    config = get_config()
    api_key = config.gemini_api_key
    
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured in AppConfig")
        raise ValueError("API key is not configured in application settings.")

    try:
        _CLIENT = Client(api_key=api_key)
        logger.info("Gemini AI client initialized successfully.")
        return _CLIENT
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI client: {str(e)}")
        raise


def get_client_with_retries() -> Client:
    """
    Creates and returns a Gemini AI client with retry capabilities.
    """
    return get_client()  # For now, just return the regular client


def get_external_call_manager() -> ExternalCallManager:
    """Get or create the external call manager for AI operations."""
    global _EXTERNAL_CALL_MANAGER
    if _EXTERNAL_CALL_MANAGER is None:
        _EXTERNAL_CALL_MANAGER = ExternalCallManager(
            timeout=60.0,  # Longer timeout for AI calls
            max_retries=3,
            base_delay=2.0,
            circuit_breaker_threshold=5,
        )
    return _EXTERNAL_CALL_MANAGER


async def generate_content_with_retries(
    prompt: str, model: str = "models/gemini-2.5-pro"
) -> Optional[str]:
    """
    Generate content using Gemini AI with timeout and retry protection.

    Args:
        prompt (str): The prompt to send to the AI
        model (str): The model to use for generation

    Returns:
        Optional[str]: Generated content or None if generation fails
    """
    manager = get_external_call_manager()

    async def ai_call():
        client = get_client()
        response = client.models.generate_content(model=model, contents=prompt)

        if response and hasattr(response, "text"):
            return response.text
        else:
            raise ValueError("AI response was empty or did not contain text")

    try:
        return await manager.call_with_retry(ai_call)
    except Exception as e:
        logging.error(
            "Error during Gemini AI API call with retries: %s", e, exc_info=True
        )
        return None


def generate_summary(text: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    Generates the analytical summary using the Gemini AI API.

    Args:
        text (str): The text to be summarized.
        api_key (str, optional): The API key for Gemini AI. If not provided, will use the key from keychain or environment.

    Returns:
        Optional[str]: Generated summary or None if generation fails.
    """
    try:
        if api_key:
            client = Client(api_key=api_key)
        else:
            client = get_client()
    except ValueError as e:
        logging.error("Failed to generate summary due to configuration error: %s", e)
        return None

    logging.info("Generating summary with AI model...")
    # Get the prompts directory from settings or use a default location
    prompts_dir = getattr(settings, "PROMPTS_DIR", Path(__file__).parent.parent / "prompts")
    prompt_path = Path(prompts_dir) / "summary_prompt.md"

    try:
        if not prompt_path.exists():
            logging.error("Prompt file not found at: %s", prompt_path)
            return None

        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(text=text)

        response = client.models.generate_content(
            model="models/gemini-2.5-pro", contents=prompt
        )

        if response and hasattr(response, "text"):
            logging.info("Summary generated successfully.")
            return response.text
        else:
            logging.warning(
                "AI response was empty or did not contain text. Details: %s", response
            )
            return None

    except Exception as e:
        logging.error("Error during Gemini AI API call: %s", e, exc_info=True)
        return None


async def generate_summary_with_retries(text: str) -> Optional[str]:
    """
    Generates the analytical summary using the Gemini AI API with retry protection.

    Args:
        text (str): The text to be summarized.

    Returns:
        Optional[str]: Generated summary or None if generation fails.
    """
    prompt_path = config.PROMPTS_DIR / "summary_prompt.md"

    try:
        if not prompt_path.exists():
            logging.error("Prompt file not found at: %s", prompt_path)
            return None

        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(text=text)

        return await generate_content_with_retries(prompt)

    except Exception as e:
        logging.error("Error preparing summary generation: %s", e, exc_info=True)
        return None
