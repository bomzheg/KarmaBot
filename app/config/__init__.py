"""
constants, settings
"""

from .karmic_triggers import (
    MINUS,
    MINUS_EMOJI,
    MINUS_TRIGGERS,
    PLUS,
    PLUS_EMOJI,
    PLUS_TRIGGERS,
    PLUS_WORDS,
)
from .main import load_config

__all__ = [
    "MINUS",
    "MINUS_EMOJI",
    "MINUS_TRIGGERS",
    "PLUS",
    "PLUS_EMOJI",
    "PLUS_TRIGGERS",
    "PLUS_WORDS",
    "load_config",
]
