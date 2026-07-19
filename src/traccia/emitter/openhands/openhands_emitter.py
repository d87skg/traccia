import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path(__file__).parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class OpenHandsEmitter:
    """Emitter for OpenHands (OS-level agent). Hooks into file/shell/browser operations."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, agent):
        """Patch an OpenHands Agent instance."""
        # OpenHands 核心方法：step, execute_action, observe
        if hasattr(agent, 'step'):
            agent.step = self._wrap_step(agent.step)
        if hasattr(agent, 'execute_action'):
            agent.execute_action = self._wrap_execute_action(agent.execute_action)
        if hasattr(agent, 'observe'):
            agent.observe = self._wrap_observe(agent.observe)
        return agent

    def _wrap_step(self, original_step):
        @functools.wraps(original_step)
        def wrapper(*args, **kwargs):
            try:
                self._recorder.observe_llm(
                    prompt="OpenHands step",
                    response="",
                    metadata={"method": "step", "runtime": "openhands"}
                )
                result = original_step(*args, **kwargs)
                self._recorder.observe_llm(
                    prompt="",
                    response=str(result),
                    metadata={"method": "step", "runtime": "openhands"}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"method": "step", "runtime": "openhands"})
                raise
        return wrapper

    def _wrap_execute_action(self, original_execute):
        @functools.wraps(original_execute)
        def wrapper(action, **kwargs):
            action_type = action.get("action", "unknown") if isinstance(action, dict) else getattr(action, 'action', 'unknown')
            try:
                # 记录不同类型的 OS 操作
                if action_type in ("run", "run_command", "shell"):
                    self._recorder.observe_tool(
                        tool_name="shell.execute",
                        input={"command": str(action.get("command", action))},
                        output={"result": "pending"},
                        metadata={"runtime": "openhands", "action": action_type}
                    )
                elif action_type in ("read", "read_file"):
                    self._recorder.observe_tool(
                        tool_name="file.read",
                        input={"path": str(action.get("path", ""))},
                        output={"result": "pending"},
                        metadata={"runtime": "openhands", "action": action_type}
                    )
                elif action_type in ("write", "write_file"):
                    self._recorder.observe_tool(
                        tool_name="file.write",
                        input={"path": str(action.get("path", "")), "size": len(str(action.get("content", "")))},
                        output={"result": "pending"},
                        metadata={"runtime": "openhands", "action": action_type}
                    )
                elif action_type in ("browse", "browser"):
                    self._recorder.observe_tool(
                        tool_name="browser.navigate",
                        input={"url": str(action.get("url", ""))},
                        output={"result": "pending"},
                        metadata={"runtime": "openhands", "action": action_type}
                    )

                result = original_execute(action, **kwargs)

                # 更新输出结果
                # 实际结果可能嵌套在 result 中，这里简化处理
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"action": action_type, "runtime": "openhands"})
                raise
        return wrapper

    def _wrap_observe(self, original_observe):
        @functools.wraps(original_observe)
        def wrapper(observation, **kwargs):
            try:
                self._recorder.observe_llm(
                    prompt="Observation",
                    response=str(observation),
                    metadata={"method": "observe", "runtime": "openhands"}
                )
                return original_observe(observation, **kwargs)
            except Exception as e:
                self._recorder.observe_error(e, {"method": "observe", "runtime": "openhands"})
                raise
        return wrapper
