# -*- coding: utf-8 -*-
# backend/cartaos/utils/text_utils.py

import unicodedata
import re
from typing import Literal

def sanitize(text: str) -> str:
    """
    Sanitize the input text.

    This function normalizes Unicode characters to avoid different representations of the same character
    and removes invisible or non-printable characters that may cause issues with the API.

    Args:
        text (str): The text to be sanitized.

    Returns:
        str: The sanitized text.
    """
    sanitized_text: str = unicodedata.normalize('NFC', text)
    sanitized_text: str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized_text)
    return sanitized_text

