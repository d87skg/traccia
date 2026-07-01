import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path("D:/Traccia/src/traccia")
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class ClaudeCodeEmitter:
    """Emitter for Claude Code (CLI agent). Hooks into shell execution and file operations."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, agent_instance):
        if hasattr(agent_instance, "run"):
            agent_instance.run = self._wrap_run(agent_instance.run)
        if hasattr(agent_instance, "execute_command"):
            agent_instance.execute_command = self._wrap_shell(agent_instance.execute_command)
        if hasattr(agent_instance, "read_file"):
            agent_instance.read_file = self._wrap_file_read(agent_instance.read_file)
        if hasattr(agent_instance, "write_file"):
            agent_instance.write_file = self._wrap_file_write(agent_instance.write_file)
        return agent_instance

    def _wrap_run(self, original_run):
        @functools.wraps(original_run)
        def wrapper(*args, **kwargs):
            try:
                result = original_run(*args, **kwargs)
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"runtime": "claude_code", "method": "run"})
                raise
        return wrapper

    def _wrap_shell(self, original_shell):
        @functools.wraps(original_shell)
        def wrapper(command, **kwargs):
            try:
                result = original_shell(command, **kwargs)
                self._recorder.observe_tool(
                    tool_name="shell.execute",
                    input={"command": command},
                    output={"result": str(result)},
                    metadata={"runtime": "claude_code"}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"command": command})
                raise
        return wrapper

    def _wrap_file_read(self, original_read):
        @functools.wraps(original_read)
        def wrapper(path, **kwargs):
            try:
                content = original_read(path, **kwargs)
                self._recorder.observe_tool(
                    tool_name="file.read",
                    input={"path": path},
                    output={"size": len(str(content))},
                    metadata={"runtime": "claude_code"}
                )
                return content
            except Exception as e:
                self._recorder.observe_error(e, {"path": path})
                raise
        return wrapper

    def _wrap_file_write(self, original_write):
        @functools.wraps(original_write)
        def wrapper(path, content, **kwargs):
            try:
                result = original_write(path, content, **kwargs)
                self._recorder.observe_tool(
                    tool_name="file.write",
                    input={"path": path, "size": len(str(content))},
                    output={"result": "success"},
                    metadata={"runtime": "claude_code"}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"path": path})
                raise
        return wrapper
