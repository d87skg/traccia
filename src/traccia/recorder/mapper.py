from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class CanonicalMapper(ABC):
    """Maps framework-specific events to canonical event types."""

    @abstractmethod
    def map(self, raw_event: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Return (canonical_type, payload)."""
        ...

class SimplePassThroughMapper(CanonicalMapper):
    """Default mapper: uses raw event_type as canonical type."""
    def map(self, raw_event: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        event_type = raw_event.get("event_type", "unknown")
        payload = raw_event.get("payload", {})
        return (event_type, payload)
