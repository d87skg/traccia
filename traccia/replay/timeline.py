"""
TRACCIA Replay API - Timeline 核心对象
"""

from typing import Any, Dict, List, Optional
from ..reference.python.utils import generate_uuid, utc_now


class TimelineEntry:
    """时间线上的单个节点"""

    def __init__(
        self,
        timestamp: str,
        event_id: str,
        event_type: str,
        title: str,
        actor_id: str,
        evidence_count: int = 0,
        summary: Optional[str] = None
    ):
        self.timestamp = timestamp
        self.event_id = event_id
        self.event_type = event_type
        self.title = title
        self.actor_id = actor_id
        self.evidence_count = evidence_count
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "title": self.title,
            "actor_id": self.actor_id,
            "evidence_count": self.evidence_count
        }
        if self.summary:
            result["summary"] = self.summary
        return result

    def __repr__(self):
        return f"TimelineEntry({self.timestamp} | {self.title})"


class Timeline:
    """Session 的可阅读视图"""

    def __init__(
        self,
        session_id: str,
        session_objective: str,
        entries: Optional[List[TimelineEntry]] = None,
        timeline_id: Optional[str] = None
    ):
        self.timeline_id = timeline_id or generate_uuid()
        self.session_id = session_id
        self.session_objective = session_objective
        self.generated_at = utc_now()
        self.entries = entries or []

    def add_entry(self, entry: TimelineEntry):
        self.entries.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeline_id": self.timeline_id,
            "session_id": self.session_id,
            "session_objective": self.session_objective,
            "generated_at": self.generated_at,
            "entries": [e.to_dict() for e in self.entries]
        }

    def __repr__(self):
        return f"Timeline({self.session_id[:8]}... | {len(self.entries)} entries)"