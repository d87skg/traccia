"""
TRACCIA AES CLI

用法：
    python -m traccia.aes resolve-session <session_id>
    python -m traccia.aes resolve-event <event_id>
    python -m traccia.aes chain <session_id>
"""

import sys
import json
from .provider import AESProvider
from .models import ResponsibilityChain, ResponsibilityLink, Actor


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m traccia.aes resolve-session <session_id>")
        print("  python -m traccia.aes resolve-event <event_id>")
        print("  python -m traccia.aes chain <session_id>")
        sys.exit(1)

    command = sys.argv[1]
    provider = AESProvider()

    if command == "resolve-session":
        if len(sys.argv) < 3:
            print("缺少 session_id")
            sys.exit(1)
        record = provider.resolve_session(sys.argv[2])
        if record:
            print(json.dumps(record.to_dict(), indent=2, ensure_ascii=False))
        else:
            print("未找到责任记录")

    elif command == "resolve-event":
        if len(sys.argv) < 3:
            print("缺少 event_id")
            sys.exit(1)
        record = provider.resolve_event(sys.argv[2])
        if record:
            print(json.dumps(record.to_dict(), indent=2, ensure_ascii=False))
        else:
            print("未找到责任记录")

    elif command == "chain":
        if len(sys.argv) < 3:
            print("缺少 session_id")
            sys.exit(1)
        # 构建示例责任链
        chain = ResponsibilityChain(session_id=sys.argv[2])
        chain.add_link(ResponsibilityLink(
            actor=Actor(id="agent_001", type="agent"),
            role="executor",
            comment="执行生成报告任务"
        ))
        chain.add_link(ResponsibilityLink(
            actor=Actor(id="operator_001", type="human"),
            role="supervisor",
            comment="监督执行过程"
        ))
        chain.add_link(ResponsibilityLink(
            actor=Actor(id="ceo_001", type="human"),
            role="approver",
            comment="最终审批"
        ))
        print(json.dumps(chain.to_dict(), indent=2, ensure_ascii=False))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()