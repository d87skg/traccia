"""
TRACCIA PROTOCOL v1 - Attribution
"""

from typing import Any, Dict, Optional
from .utils import generate_uuid, validate_required_fields

ATTRIBUTION_REQUIRED = ["attribution_id", "session_id", "executor"]


class Attribution:
    """
    Attribution：将行为与责任主体绑定。

    Traccia 负责记录结构，AES 负责解释责任。

    字段：
    - executor: 执行者（必填）
    - supervisor: 监督者（可选，预留给AES）
    - approver: 批准者（可选，预留给AES）
    - policy_id: 适用策略ID（可选，预留给AES）
    """

    def __init__(
        self,
        session_id: str,
        executor: str,
        supervisor: Optional[str] = None,
        approver: Optional[str] = None,
        policy_id: Optional[str] = None,
        attribution_id: Optional[str] = None
    ):
        self.attribution_id = attribution_id or generate_uuid()
        self.session_id = session_id
        self.executor = executor
        self.supervisor = supervisor
        self.approver = approver
        self.policy_id = policy_id

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "attribution_id": self.attribution_id,
            "session_id": self.session_id,
            "executor": self.executor
        }
        if self.supervisor:
            result["supervisor"] = self.supervisor
        if self.approver:
            result["approver"] = self.approver
        if self.policy_id:
            result["policy_id"] = self.policy_id
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribution":
        validate_required_fields(data, ATTRIBUTION_REQUIRED)
        return cls(
            session_id=data["session_id"],
            executor=data["executor"],
            supervisor=data.get("supervisor"),
            approver=data.get("approver"),
            policy_id=data.get("policy_id"),
            attribution_id=data["attribution_id"]
        )

    def __repr__(self):
        return f"Attribution({self.attribution_id[:8]}... | executor={self.executor})"