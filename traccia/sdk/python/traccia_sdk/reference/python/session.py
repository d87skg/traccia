"""
TRACCIA PROTOCOL v1 - Session
"""

from typing import Any, Dict, Optional
from .utils import generate_uuid, utc_now, validate_required_fields

SESSION_REQUIRED = ["session_id", "objective", "started_at", "status"]
VALID_STATUSES = {"running", "completed", "failed", "cancelled"}


class Session:
    """
    Session：一个完整目标的执行上下文。

    字段：
    - session_id: 全局唯一标识
    - objective: 目标描述
    - started_at: 开始时间
    - ended_at: 结束时间（可选）
    - status: running | completed | failed | cancelled
    """

    def __init__(
        self,
        objective: str,
        session_id: Optional[str] = None,
        started_at: Optional[str] = None,
        status: str = "running"
    ):
        self.session_id = session_id or generate_uuid()
        self.objective = objective
        self.started_at = started_at or utc_now()
        self.ended_at: Optional[str] = None
        self.status = status

        if self.status not in VALID_STATUSES:
            raise ValueError(f"无效的 status: {self.status}，允许值: {VALID_STATUSES}")

    def complete(self):
        """标记 Session 完成"""
        self.status = "completed"
        self.ended_at = utc_now()

    def fail(self):
        """标记 Session 失败"""
        self.status = "failed"
        self.ended_at = utc_now()

    def cancel(self):
        """标记 Session 取消"""
        self.status = "cancelled"
        self.ended_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        result = {
            "session_id": self.session_id,
            "objective": self.objective,
            "started_at": self.started_at,
            "status": self.status
        }
        if self.ended_at:
            result["ended_at"] = self.ended_at
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """从字典反序列化"""
        validate_required_fields(data, SESSION_REQUIRED)
        session = cls(
            session_id=data["session_id"],
            objective=data["objective"],
            started_at=data["started_at"],
            status=data["status"]
        )
        if "ended_at" in data:
            session.ended_at = data["ended_at"]
        return session

    def __repr__(self):
        return f"Session({self.session_id[:8]}... | {self.objective[:30]} | {self.status})"