"""
AES Research Workload — Traccia 集成

用法：
    python research_log.py "研究主题" [报告文件路径]

示例：
    python research_log.py "Analyze Traccia Protocol" reports/traccia-v1.1.md
"""

import sys
import hashlib
from pathlib import Path

# 引入 SDK
sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia_sdk import start

def main():
    if len(sys.argv) < 2:
        print("用法: python research_log.py <研究主题> [报告文件路径]")
        sys.exit(1)

    topic = sys.argv[1]
    report_path = sys.argv[2] if len(sys.argv) > 2 else None

    # 创建 Session
    session = start(objective=f"Research: {topic}")
    
    # 记录 LLM 交互（实际可扩展为从对话历史中提取）
    session.record("llm.prompt", payload={"topic": topic})
    session.record("llm.response", payload={"note": "研究完成"})
    
    # 如果有报告文件，作为 Evidence 添加
    if report_path and Path(report_path).exists():
        content = Path(report_path).read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        session.add_evidence(
            session._events[-1],  # 关联最后一个事件
            evidence_type="file_hash",
            sha256_hash=file_hash,
            storage_uri=f"file:///{Path(report_path).absolute().as_posix()}"
        )
    else:
        # 即使没有报告，也记录一个空 evidence 保持结构完整
        session.add_evidence(
            session._events[-1],
            evidence_type="api_response",
            sha256_hash="",
            storage_uri="none"
        )

    session.finish()
    
    # 导出到 evidence 目录
    evidence_dir = Path("D:/Traccia/evidence")
    evidence_dir.mkdir(exist_ok=True)
    output = evidence_dir / f"research-{Path(topic).stem[:30]}-{session.session_id[:8]}.evidence"
    session.export(str(output))
    
    print(f"Research Package: {output}")
    print(f"Session: {session.session_id[:12]}...")
    print(f"Verify: ", end="")
    from traccia_sdk.reference.python.validator import verify
    result = verify(str(output))
    print(result.status)
    if not result.is_valid:
        print(result.report())

if __name__ == "__main__":
    main()