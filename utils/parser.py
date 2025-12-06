# File: utils/parser.py
"""Parser utilities for Virtual Memory Simulator.

Provides functions to parse a user-provided page reference string into a
list of non-negative integers and to validate the number of frames.

Public API:
- parse_reference_string(s: str, max_length: int = 2000) -> list[int]
- validate_frames(n: Any, min_frames: int = 1, max_frames: int = 100) -> int
- parse_and_validate(ref: str, frames_input: Any, max_length: int = 2000, min_frames: int = 1, max_frames: int = 100) -> tuple[list[int], int]

The functions raise ValueError with clear messages on invalid input so the UI
can display user-friendly errors.
"""
from __future__ import annotations

import re
from typing import Any, List, Tuple


def _tokenize(s: str) -> List[str]:
    """Split the input string into tokens using commas and whitespace.

    Keeps empty tokens removed.
    """
    if s is None:
        return []
    # split on commas or any whitespace
    raw = re.split(r"[\s,]+", s.strip())
    return [t for t in raw if t != ""]


def parse_reference_string(s: str, max_length: int = 2000) -> List[int]:
    """Parse a reference string into a list of non-negative integers.

    Accepts numbers separated by spaces and/or commas. Raises ValueError when
    the input contains invalid tokens, negative numbers, or when the resulting
    list is empty or longer than max_length.
    """
    tokens = _tokenize(s)

    if not tokens:
        raise ValueError("Reference string is empty. Enter page numbers separated by spaces or commas.")

    if len(tokens) > max_length:
        raise ValueError(f"Reference string too long ({len(tokens)} entries). Maximum allowed is {max_length}.")

    pages: List[int] = []
    for idx, tok in enumerate(tokens):
        # Reject tokens that are not a pure non-negative integer
        if not re.fullmatch(r"\d+", tok):
            # Provide position (1-based) and token in message for better UX
            raise ValueError(f"Invalid token '{tok}' at position {idx+1}. Use only non-negative integers separated by spaces or commas.")
        # safe to convert
        val = int(tok)
        # Disallow negative numbers (regex already ensures non-negative) but keep the check for safety
        if val < 0:
            raise ValueError(f"Negative page number '{tok}' at position {idx+1} is not allowed.")
        pages.append(val)

    if len(pages) == 0:
        raise ValueError("Reference string parsing produced no pages.")

    return pages


def validate_frames(n: Any, min_frames: int = 1, max_frames: int = 100) -> int:
    """Validate and normalize frames input.

    Accepts integers or strings that contain an integer (e.g., "3"). Raises ValueError
    for non-integers or values outside [min_frames, max_frames].
    Returns the validated int.
    """
    # Try converting to int
    try:
        val = int(n)
    except Exception:
        raise ValueError(f"Frames must be an integer between {min_frames} and {max_frames}.")

    if val < min_frames or val > max_frames:
        raise ValueError(f"Frames must be between {min_frames} and {max_frames}.")

    return val


def parse_and_validate(ref: str, frames_input: Any, max_length: int = 2000, min_frames: int = 1, max_frames: int = 100) -> Tuple[List[int], int]:
    """Convenience function that returns (pages_list, frames_int).

    Raises ValueError with clear messages on any invalid input.
    """
    pages = parse_reference_string(ref, max_length=max_length)
    frames = validate_frames(frames_input, min_frames=min_frames, max_frames=max_frames)
    return pages, frames


# ---------------------------
# File: tests/test_parser.py
# ---------------------------

# Tests for utils/parser.py

