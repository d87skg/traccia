"""
TRACCIA Replay API - Filters

Timeline 过滤器
"""

from typing import Optional
from .timeline import Timeline, TimelineEntry


class TimelineFilter:
    """Timeline 过滤器"""

    def filter(
        self,
        timeline: Timeline,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Timeline:
        """
        过滤 Timeline，返回新的 Timeline 对象。

        Args:
            timeline: 原始 Timeline
            event_type: 按事件类型过滤
            actor_id: 按执行者过滤
            start_time: 起始时间（ISO 8601）
            end_time: 结束时间（ISO 8601）

        Returns:
            过滤后的 Timeline
        """
        filtered = Timeline(
            session_id=timeline.session_id,
            session_objective=timeline.session_objective
        )

        for entry in timeline.entries:
            if event_type and entry.event_type != event_type:
                continue
            if actor_id and entry.actor_id != actor_id:
                continue
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            filtered.add_entry(entry)

        return filtered