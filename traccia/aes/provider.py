"""
TRACCIA AES Adapter - AttributionProvider 接口与 AES 实现
"""

from abc import ABC, abstractmethod
from typing import Optional
from .models import ResponsibilityRecord


class AttributionProvider(ABC):
    """
    责任归属提供者（抽象接口）。

    Traccia 定义此接口，不依赖任何特定实现。
    AES 只是其中一种实现。
    """

    @abstractmethod
    def resolve_session(self, session_id: str) -> Optional[ResponsibilityRecord]:
        """解析 Session 的责任归属"""
        ...

    @abstractmethod
    def resolve_event(self, event_id: str) -> Optional[ResponsibilityRecord]:
        """解析 Event 的责任归属"""
        ...


class AESProvider(AttributionProvider):
    """
    AES 责任归属提供者（Stub 实现）。

    当前为存根实现，返回模拟数据。
    生产环境需接入真实 AES 服务端点。
    """

    def __init__(self, aes_endpoint: str = "http://localhost:8080"):
        self.aes_endpoint = aes_endpoint

    def resolve_session(self, session_id: str) -> Optional[ResponsibilityRecord]:
        """
        解析 Session 责任。

        存根实现：返回示例数据。
        生产实现：调用 AES API。
        """
        # Stub: 模拟 AES 响应
        from .models import Actor
        return ResponsibilityRecord(
            subject_id=session_id,
            subject_type="session",
            executor=Actor(id="agent_001", type="agent"),
            supervisor=Actor(id="operator_001", type="human"),
            approver=Actor(id="ceo_001", type="human"),
            policy_id="AES-RISK-001",
            risk_level="medium"
        )

    def resolve_event(self, event_id: str) -> Optional[ResponsibilityRecord]:
        """
        解析 Event 责任。

        存根实现：返回示例数据。
        生产实现：调用 AES API。
        """
        from .models import Actor
        return ResponsibilityRecord(
            subject_id=event_id,
            subject_type="event",
            executor=Actor(id="agent_001", type="agent"),
            risk_level="low"
        )