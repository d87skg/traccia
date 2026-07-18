"""
OpenBase Adapter — Protocol compliance layer for Traccia SDK.
"""

from .event_mapper import to_obs, is_valid_obs, TRACCIA_TO_OBS, OBS_EVENT_TYPES
from .evidence_converter import convert, batch_convert
from .signer import OpenBaseSignerBridge

__all__ = [
    "to_obs",
    "is_valid_obs",
    "TRACCIA_TO_OBS",
    "OBS_EVENT_TYPES",
    "convert",
    "batch_convert",
    "OpenBaseSignerBridge",
]
