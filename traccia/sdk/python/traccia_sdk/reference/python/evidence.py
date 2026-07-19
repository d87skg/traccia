"""
TRACCIA PROTOCOL v1 - Evidence
"""

from typing import Any, Dict, Optional
from .utils import generate_uuid, utc_now, validate_required_fields

EVIDENCE_REQUIRED = [
    "evidence_id", "event_id", "type",
    "sha256", "storage_uri", "created_at"
]

VALID_EVIDENCE_TYPES = {
    "file_hash", "screenshot", "api_response",
    "log_snapshot", "binary_blob"
}


class Evidence:
    """
    Evidence：证明Event真实发生的材料。

    核心原则：No Evidence = No Trust
    """

    def __init__(
        self,
        event_id: str,
        evidence_type: str,
        sha256_hash: str,
        storage_uri: str,
        evidence_id: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        if evidence_type not in VALID_EVIDENCE_TYPES:
            raise ValueError(f"无效的 evidence type: {evidence_type}，允许值: {VALID_EVIDENCE_TYPES}")

        self.evidence_id = evidence_id or generate_uuid()
        self.event_id = event_id
        self.type = evidence_type
        self.sha256 = sha256_hash
        self.storage_uri = storage_uri
        self.created_at = created_at or utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "event_id": self.event_id,
            "type": self.type,
            "sha256": self.sha256,
            "storage_uri": self.storage_uri,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        validate_required_fields(data, EVIDENCE_REQUIRED)
        return cls(
            event_id=data["event_id"],
            evidence_type=data["type"],
            sha256_hash=data["sha256"],
            storage_uri=data["storage_uri"],
            evidence_id=data["evidence_id"],
            created_at=data["created_at"]
        )

    def __repr__(self):
        return f"Evidence({self.evidence_id[:8]}... -> Event({self.event_id[:8]}...) | {self.type})"