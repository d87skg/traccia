"""
TRACCIA Replay API - Renderer

Timeline → 多格式输出
"""

import json
from .timeline import Timeline


class TimelineRenderer:
    """Timeline 多格式渲染器"""

    def render(self, timeline: Timeline, format: str = "text") -> str:
        if format == "json":
            return self._render_json(timeline)
        elif format == "md" or format == "markdown":
            return self._render_markdown(timeline)
        else:
            return self._render_text(timeline)

    def _render_text(self, timeline: Timeline) -> str:
        """纯文本渲染"""
        lines = []
        lines.append(f"Session: {timeline.session_objective}")
        lines.append("─" * 50)

        if not timeline.entries:
            lines.append("(无事件)")
            return "\n".join(lines)

        for entry in timeline.entries:
            # 提取时间部分 HH:MM:SS
            time_str = self._format_time(entry.timestamp)
            evidence_info = f"Evidence: {entry.evidence_count}" if entry.evidence_count > 0 else ""
            lines.append(f"\n[{time_str}] {entry.title}")
            if entry.summary:
                lines.append(f"           {entry.summary}")
            if evidence_info:
                lines.append(f"           {evidence_info}")

        return "\n".join(lines)

    def _render_markdown(self, timeline: Timeline) -> str:
        """Markdown 渲染"""
        lines = []
        lines.append(f"# Session: {timeline.session_objective}")
        lines.append("")
        lines.append("## Timeline")
        lines.append("")

        if not timeline.entries:
            lines.append("*(无事件)*")
            return "\n".join(lines)

        for entry in timeline.entries:
            time_str = self._format_time(entry.timestamp)
            lines.append(f"### {time_str} — {entry.title}")
            lines.append("")
            lines.append(f"- **Type**: `{entry.event_type}`")
            lines.append(f"- **Actor**: `{entry.actor_id}`")
            if entry.summary:
                lines.append(f"- **Summary**: {entry.summary}")
            if entry.evidence_count > 0:
                lines.append(f"- **Evidence**: {entry.evidence_count}")
            lines.append("")

        return "\n".join(lines)

    def _render_json(self, timeline: Timeline) -> str:
        """JSON 渲染"""
        return json.dumps(timeline.to_dict(), indent=2, ensure_ascii=False)

    def _format_time(self, timestamp: str) -> str:
        """从 ISO 8601 时间戳提取 HH:MM:SS"""
        try:
            # 格式: 2026-06-08T12:00:01Z 或 2026-06-08T12:00:01.123456Z
            if "T" in timestamp:
                time_part = timestamp.split("T")[1]
                # 去掉毫秒和时区
                time_part = time_part.split(".")[0].replace("Z", "")
                return time_part
        except Exception:
            pass
        return timestamp