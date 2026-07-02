#!/usr/bin/env python3
"""
traccia — AI Agent 行为闭环控制 CLI

用法:
    traccia intercept -- python my_agent.py
    traccia diagnose task.evidence
    traccia loop run [--iterations N]
"""

import sys
import os
import subprocess
from pathlib import Path

# 确保能找到核心模块
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "traccia"))
sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def cmd_intercept(args):
    """拦截模式：包装目标进程，自动记录"""
    if not args:
        print("用法: traccia intercept -- <command>")
        sys.exit(1)

    cmd_str = " ".join(args)
    print(f"Traccia intercepting: {cmd_str}")
    from traccia import start
    session = start(objective=f"intercept: {cmd_str}")
    session.record("process.start", payload={"command": args})

    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=300)
        session.record("process.exit", payload={
            "returncode": result.returncode,
            "stdout": result.stdout[:1000],
            "stderr": result.stderr[:1000]
        })
    except Exception as e:
        session.record("process.error", payload={"error": str(e)})

    session.finish()
    evidence_path = f"traccia-{session.session_id[:8]}.evidence"
    session.export(evidence_path)
    print(f"Evidence saved: {evidence_path}")
    print(f"👉 Next: traccia diagnose {evidence_path}")

def cmd_diagnose(args):
    """诊断模式：分析证据包"""
    if not args:
        print("用法: traccia diagnose <file.evidence>")
        sys.exit(1)

    evidence_file = args[0]
    if not os.path.exists(evidence_file):
        print(f"File not found: {evidence_file}")
        sys.exit(1)

    sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "traccia"))
    from analyzer.engine import analyze
    result = analyze(evidence_file)

    print("=" * 50)
    print("📊 诊断报告")
    print("=" * 50)
    print(f"文件: {evidence_file}")
    print(f"验证: {'✅ 有效' if result.get('valid') else '❌ 无效'}")
    print(f"异常事件数: {result.get('errors_found', 0)}")
    print("\n根本原因分析:")
    for cause in result.get('root_causes', []):
        print(f"  • {cause['category']} (置信度: {cause['confidence']})")
    print(f"\n{result.get('summary', '无结论')}")

def cmd_loop(args):
    """闭环模式：运行 residual 反馈循环"""
    if not args or args[0] != "run":
        print("用法: traccia loop run [--iterations N]")
        sys.exit(1)

    iterations = 5
    if "--iterations" in args:
        try:
            idx = args.index("--iterations")
            iterations = int(args[idx + 1])
        except (IndexError, ValueError):
            print("Invalid iterations argument")
            sys.exit(1)

    # 确保 loop 模块路径
    loop_module_path = Path(__file__).parent.parent / "src" / "traccia" / "loop"
    sys.path.insert(0, str(loop_module_path.parent))
    from loop.loop import run_loop
    run_loop(iterations=iterations)

def main():
    if len(sys.argv) < 2:
        print("traccia intercept -- <command>")
        print("traccia diagnose <file.evidence>")
        print("traccia loop run [--iterations N]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "intercept":
        if args and args[0] == "--":
            args = args[1:]
        cmd_intercept(args)
    elif command == "diagnose":
        cmd_diagnose(args)
    elif command == "loop":
        cmd_loop(args)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()