import sys, json, zipfile
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")

from recorder import DefaultRecorder

def stress_test(runtime_name, recorder, inject_failures=True):
    """注入故障模式：超时、权限拒绝、循环、无效操作。"""
    # 1. 正常操作
    recorder.observe_llm("Hello", "Hi", {"runtime": runtime_name})
    recorder.observe_tool("search", {"q": "test"}, {"result": "found"}, {"runtime": runtime_name})
    
    if inject_failures:
        # 2. 超时故障
        recorder.observe_error(
            TimeoutError("Connection timed out after 30s"),
            {"runtime": runtime_name, "action": "tool_call"}
        )
        # 3. 权限拒绝
        recorder.observe_error(
            PermissionError("Permission denied: /etc/shadow"),
            {"runtime": runtime_name, "action": "file.read"}
        )
        # 4. 循环模式（连续重复事件）
        for i in range(5):
            recorder.observe_tool("retry", {"attempt": i+1}, {"result": "failed"}, {"runtime": runtime_name})
        # 5. 恢复：重新规划
        recorder.observe_llm("", "Replanning due to failures", {"runtime": runtime_name, "action": "replan"})
        # 6. 无效操作（模拟hallucinated tool）
        recorder.observe_error(
            AttributeError("No such tool: invalid_function"),
            {"runtime": runtime_name, "action": "tool.invoke"}
        )
    
    # 完成
    recorder.finish()
    return recorder.export(f"tests/integration/stress_{runtime_name}.evidence")

# 为6个Runtime生成压力测试证据
runtimes = ["langchain", "crewai", "autogen", "openai", "claude_code", "openhands"]
for rt in runtimes:
    recorder = DefaultRecorder(f"Stress Test: {rt}")
    path = stress_test(rt, recorder)
    print(f"Generated: {path}")

print("Chaos test suite generated.")
