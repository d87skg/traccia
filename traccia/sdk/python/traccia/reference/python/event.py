"""
TRACCIA PROTOCOL v1 - Event
"""

from typing import Any, Dict, Optional
from .utils import generate_uuid, utc_now, sha256_hex, dict_to_json_stable, validate_required_fields

EVENT_REQUIRED = [
    "event_id", "session_id", "timestamp",
    "event_type", "actor_id", "payload",
    "prev_hash", "hash"
]


class Event:
    """
    Event：一个不可再分的、可验证的原子行为事实。

    三原则：
    1. Atomic - 不可再拆
    2. Immutable - 一旦生成，永远存在
    3. Time Ordered - 必须存在时间顺序

    HashChain 算法：
        hash_n = SHA-256( prev_hash + event_content_json )
        创世Event：prev_hash = None
    """

    def __init__(
        self,
        session_id: str,
        event_type: str,
        actor_id: str,
        payload: Dict[str, Any],
        prev_hash: Optional[str] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.event_id = event_id or generate_uuid()
        self.session_id = session_id
        self.timestamp = timestamp or utc_now()
        self.event_type = event_type
        self.actor_id = actor_id
        self.payload = payload
        self.prev_hash = prev_hash
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """计算本Event的SHA-256哈希"""
        content_json = self._content_json()
        prefix = self.prev_hash or ""
        combined = prefix + content_json
        return sha256_hex(combined)

    def _content_json(self) -> str:
        """返回不含hash字段的Event内容JSON，用于hash计算"""
        content = {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "payload": self.payload,
            "prev_hash": self.prev_hash
        }
        return dict_to_json_stable(content)

    def verify_chain_link(self, prev_event: Optional["Event"]) -> bool:
        """验证与前一事件的链上关系"""
        if prev_event is None:
            return self.prev_hash is None
        else:
            return self.prev_hash == prev_event.hash

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """从字典反序列化，会重新计算hash以验证完整性"""
        validate_required_fields(data, EVENT_REQUIRED)
        event = cls(
            session_id=data["session_id"],
            event_type=data["event_type"],
            actor_id=data["actor_id"],
            payload=data["payload"],
            prev_hash=data["prev_hash"],
            event_id=data["event_id"],
            timestamp=data["timestamp"]
        )
        if event.hash != data["hash"]:
            raise ValueError(f"Event hash 不一致！")
        return event

    def __repr__(self):
        return f"Event({self.event_id[:8]}... | {self.event_type} | hash={self.hash[:12]}...)"