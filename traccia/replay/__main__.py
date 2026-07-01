"""
TRACCIA Replay CLI

用法：
    python -m traccia.replay task.evidence
    python -m traccia.replay task.evidence --format md
    python -m traccia.replay task.evidence --format json
    python -m traccia.replay task.evidence --event-type api_call
    python -m traccia.replay task.evidence --actor agent_001
"""

import sys
import argparse
from ..reference.python.validator import verify
from ..reference.python.package import Package
from ..reference.python import Session, Event, Evidence, Attribution
from .builder import ReplayBuilder
from .renderer import TimelineRenderer
from .filters import TimelineFilter


def load_package(filepath: str) -> Package:
    """从 task.evidence 加载 Package"""
    import zipfile
    import json

    with zipfile.ZipFile(filepath, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))
        session_data = json.loads(zf.read("session.json"))

        events_data = []
        events_text = zf.read("events.jsonl").decode("utf-8")
        for line in events_text.strip().split("\n"):
            if line.strip():
                events_data.append(json.loads(line))

        evidence_data = []
        if "evidence.json" in zf.namelist():
            evidence_data = json.loads(zf.read("evidence.json"))

        attribution_data = None
        if "attribution.json" in zf.namelist():
            attribution_data = json.loads(zf.read("attribution.json"))

    session = Session.from_dict(session_data)
    events = [Event.from_dict(e) for e in events_data]
    evidence_list = [Evidence.from_dict(e) for e in evidence_data]
    attribution = Attribution.from_dict(attribution_data) if attribution_data else None

    return Package(
        session=session,
        events=events,
        evidence_list=evidence_list,
        attribution=attribution
    )


def main():
    parser = argparse.ArgumentParser(description="Traccia Replay - 重建事实")
    parser.add_argument("package", help="task.evidence 文件路径")
    parser.add_argument("--format", "-f", choices=["text", "md", "markdown", "json"],
                        default="text", help="输出格式 (默认: text)")
    parser.add_argument("--event-type", "-e", help="按事件类型过滤")
    parser.add_argument("--actor", "-a", help="按执行者过滤")
    parser.add_argument("--verify-only", action="store_true", help="仅验证，不回放")

    args = parser.parse_args()

    # 先验证
    result = verify(args.package)
    if not result.is_valid:
        print(result.report())
        sys.exit(1)

    if args.verify_only:
        print(result.report())
        return

    # 加载 Package
    package = load_package(args.package)

    # 构建 Timeline
    builder = ReplayBuilder()
    timeline = builder.build(package)

    # 过滤
    if args.event_type or args.actor:
        timeline_filter = TimelineFilter()
        timeline = timeline_filter.filter(
            timeline,
            event_type=args.event_type,
            actor_id=args.actor
        )

    # 渲染
    renderer = TimelineRenderer()
    output = renderer.render(timeline, format=args.format)
    print(output)


if __name__ == "__main__":
    main()