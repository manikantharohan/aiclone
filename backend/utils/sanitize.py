"""
Input sanitization for user messages.
"""
from __future__ import annotations

import re
from typing import Optional

# Max length for a single user message (chars)
MAX_MESSAGE_LENGTH = 16_000


def sanitize_user_input(raw: Optional[str]) -> str:
    """
    Sanitize user input: strip, truncate, and normalize whitespace.
    Returns empty string if input is None or invalid.
    """
    if raw is None:
        return ""
    if not isinstance(raw, str):
        return ""
    s = raw.strip()
    # Collapse multiple spaces/newlines into single space
    s = re.sub(r"\s+", " ", s)
    if len(s) > MAX_MESSAGE_LENGTH:
        s = s[:MAX_MESSAGE_LENGTH]
    return s
