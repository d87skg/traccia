import sys, json
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")

from recorder import DefaultRecorder

def inject_runtime_events(recorder, runtime):
    """为不同 Runtime 注入专属事件类型。"""
    # 1. 正常操作
    recorder._record_event("llm.request", {"prompt": "Hello", "response": "Hi", "runtime": runtime})
    
    # 2. 注入 Runtime-specific 工具调用
    if runtime in ("claude_code", "openhands"):
        recorder._record_event("shell.execute", {"command": "ls -la", "runtime": runtime})
        recorder._record_event("file.read", {"path": "/etc/config", "runtime": runtime})
        if runtime == "openhands":
            recorder._record_event("browser.navigate", {"url": "https://example.com", "runtime": runtime})
    elif runtime == "langchain":
        recorder._record_event("tool.invoke", {"tool": "search", "input": "query", "runtime": runtime})
        recorder._record_event("tool.result", {"result": "found", "runtime": runtime})
    elif runtime == "crewai":
        recorder._record_event("agent.delegate", {"from": "Researcher", "to": "Writer", "runtime": runtime})
        recorder._record_event("tool.invoke", {"tool": "search", "runtime": runtime})
    elif runtime == "autogen":
        recorder._record_event("message.send", {"sender": "Agent1", "receiver": "Agent2", "content": "Hello", "runtime": runtime})
    elif runtime == "openai":
        recorder._record_event("function.call", {"name": "get_weather", "arguments": {"location": "Tokyo"}, "runtime": runtime})
    
    # 3. 故障注入（同前）
    recorder.observe_error(TimeoutError("Connection timed out"), {"runtime": runtime, "action": "tool_call"})
    recorder.observe_error(PermissionError("Permission denied"), {"runtime": runtime, "action": "file.read"})
    for i in range(3):
        recorder.observe_tool("retry", {"attempt": i+1}, {"result": "failed"}, {"runtime": runtime})
    recorder.observe_llm("", "Replanning due to failures", {"runtime": runtime, "action": "replan"})
    recorder.observe_error(AttributeError("No such tool: invalid_function"), {"runtime": runtime})

# 生成 6 个 Runtime 的差异化压力包
runtimes = ["langchain", "crewai", "autogen", "openai", "claude_code", "openhands"]
for rt in runtimes:
    recorder = DefaultRecorder(f"Stress Diversity: {rt}")
    inject_runtime_events(recorder, rt)
    recorder.finish()
    path = recorder.export(f"tests/integration/diversity_{rt}.evidence")
    print(f"Generated: {path}")

print("Diversity injection complete.")
