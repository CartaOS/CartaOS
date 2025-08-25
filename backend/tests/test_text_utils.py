# -*- coding: utf-8 -*-
# backend/tests/test_text_utils.py

import pytest

from cartaos.utils.text_utils import sanitize


def test_sanitize_removes_control_characters():
    s = "Hello\x00World\x1f!\x7f\x90"
    out = sanitize(s)
    assert out == "HelloWorld!"


def test_sanitize_normalizes_unicode_nfc():
    # 'e' + combining acute vs precomposed 'é'
    combining = "e\u0301"  # e + ́
    precomposed = "é"
    # After sanitize both should be equal in NFC form
    out1 = sanitize(combining)
    out2 = sanitize(precomposed)
    assert out1 == out2 == "é"
