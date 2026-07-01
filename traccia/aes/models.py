"""
TRACCIA AES Adapter - 核心数据模型
"""

from typing import Optional, List
from dataclasses import dataclass, field
from ..reference.python.utils import generate_uuid, utc_now


@dataclass
class Actor:
    """责任主体"""
    id: str
    type: str  # "agent" | "human" | "workflow" | "committee"

    def to_dict(self) -> dict:
        return {"id": self.id, "type": self.type}

    @classmethod
    def from_dict(cls, data: dict) -> "Actor":
        # 兼容 v1 扁平格式（纯字符串）
        if isinstance(data, str):
            return cls(id=data, type="unknown")
        return cls(id=data["id"], type=data.get("type", "unknown"))

    def __repr__(self):
        return f"{self.type}:{self.id}"


@dataclass
class ResponsibilityRecord:
    """责任解析记录"""
    subject_id: str
    subject_type: str  # "session" | "event"
    executor: Actor
    supervisor: Optional[Actor] = None
    approver: Optional[Actor] = None
    policy_id: Optional[str] = None
    risk_level: str = "medium"
    record_id: Optional[str] = None
    resolved_at: Optional[str] = None

    def __post_init__(self):
        self.record_id = self.record_id or generate_uuid()
        self.resolved_at = self.resolved_at or utc_now()

    def to_dict(self) -> dict:
        result = {
            "record_id": self.record_id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "executor": self.executor.to_dict(),
            "risk_level": self.risk_level,
            "resolved_at": self.resolved_at
        }
        if self.supervisor:
            result["supervisor"] = self.supervisor.to_dict()
        if self.approver:
            result["approver"] = self.approver.to_dict()
        if self.policy_id:
            result["policy_id"] = self.policy_id
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ResponsibilityRecord":
        return cls(
            record_id=data.get("record_id"),
            subject_id=data["subject_id"],
            subject_type=data["subject_type"],
            executor=Actor.from_dict(data["executor"]),
            supervisor=Actor.from_dict(data["supervisor"]) if data.get("supervisor") else None,
            approver=Actor.from_dict(data["approver"]) if data.get("approver") else None,
            policy_id=data.get("policy_id"),
            risk_level=data.get("risk_level", "medium"),
            resolved_at=data.get("resolved_at")
        )


@dataclass
class ResponsibilityLink:
    """责任链上的一个环节"""
    actor: Actor
    role: str  # "executor" | "supervisor" | "approver"
    timestamp: Optional[str] = None
    comment: Optional[str] = None

    def __post_init__(self):
        self.timestamp = self.timestamp or utc_now()

    def to_dict(self) -> dict:
        result = {
            "actor": self.actor.to_dict(),
            "role": self.role,
            "timestamp": self.timestamp
        }
        if self.comment:
            result["comment"] = self.comment
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ResponsibilityLink":
        return cls(
            actor=Actor.from_dict(data["actor"]),
            role=data["role"],
            timestamp=data.get("timestamp"),
            comment=data.get("comment")
        )


@dataclass
class ResponsibilityChain:
    """一个 Session 内的责任链"""
    session_id: str
    links: List[ResponsibilityLink] = field(default_factory=list)
    chain_id: Optional[str] = None

    def __post_init__(self):
        self.chain_id = self.chain_id or generate_uuid()

    def add_link(self, link: ResponsibilityLink):
        self.links.append(link)

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "session_id": self.session_id,
            "links": [l.to_dict() for l in self.links]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResponsibilityChain":
        chain = cls(
            chain_id=data.get("chain_id"),
            session_id=data["session_id"]
        )
        for link_data in data.get("links", []):
            chain.add_link(ResponsibilityLink.from_dict(link_data))
        return chain