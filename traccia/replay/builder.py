"""
TRACCIA Replay API - Builder

Package → Timeline 转换
"""

from typing import Dict
from .timeline import Timeline, TimelineEntry
from ..reference.python.package import Package


# 内置 event_type → 人类可读标题映射
EVENT_TITLE_MAP: Dict[str, str] = {
    "read_file": "读取文件",
    "write_file": "写入文件",
    "api_call": "API 调用",
    "generate_response": "生成回复",
    "execute_shell": "执行 Shell 命令",
    "click_button": "点击按钮",
    "user_input": "用户输入",
    "approval_request": "请求审批",
    "approval_granted": "审批通过",
    "approval_denied": "审批拒绝",
}


class ReplayBuilder:
    """从 Package 构建 Timeline"""

    def __init__(self, title_map: Dict[str, str] | None = None):
        self.title_map = title_map or EVENT_TITLE_MAP

    def build(self, package: Package) -> Timeline:
        """从 Package 构建 Timeline"""
        timeline = Timeline(
            session_id=package.session.session_id,
            session_objective=package.session.objective
        )

        # 构建 evidence 查找表：event_id → evidence count
        evidence_map: Dict[str, int] = {}
        for ev in package.evidence_list:
            evidence_map[ev.event_id] = evidence_map.get(ev.event_id, 0) + 1

        # 构建 entries
        for event in package.events:
            title = self._get_title(event.event_type)
            evidence_count = evidence_map.get(event.event_id, 0)

            entry = TimelineEntry(
                timestamp=event.timestamp,
                event_id=event.event_id,
                event_type=event.event_type,
                title=title,
                actor_id=event.actor_id,
                evidence_count=evidence_count,
                summary=self._build_summary(event.event_type, event.payload)
            )
            timeline.add_entry(entry)

        return timeline

    def _get_title(self, event_type: str) -> str:
        """获取人类可读标题"""
        return self.title_map.get(event_type, event_type)

    def _build_summary(self, event_type: str, payload: dict) -> str:
        """根据事件类型和 payload 构建摘要"""
        if event_type == "read_file":
            return f"读取了 {payload.get('file_path', '未知文件')}"
        elif event_type == "write_file":
            return f"写入了 {payload.get('file_path', '未知文件')}"
        elif event_type == "api_call":
            return f"调用了 {payload.get('endpoint', '未知接口')}"
        elif event_type == "generate_response":
            return f"生成了 {payload.get('format', '')} 格式的 {payload.get('output_type', '回复')}"
        elif event_type == "execute_shell":
            return f"执行命令: {payload.get('command', '未知')}"
        else:
            return ""