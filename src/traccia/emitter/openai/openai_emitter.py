import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path('D:/Traccia/src/traccia')
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class OpenAIEmitter:
    """Emitter for OpenAI Agent SDK. Patches Agent to record LLM and tool events."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, agent):
        """Patch an OpenAI Agent instance."""
        # Patch the main run method
        if hasattr(agent, 'run'):
            original_run = agent.run
            agent.run = self._wrap_run(original_run, agent)

        # Patch function_call if present (some versions use execute)
        if hasattr(agent, 'execute_tool'):
            original_tool = agent.execute_tool
            agent.execute_tool = self._wrap_tool(original_tool)

        if hasattr(agent, 'function_call'):
            original_func = agent.function_call
            agent.function_call = self._wrap_tool(original_func)

        return agent

    def _wrap_run(self, original_run, agent):
        @functools.wraps(original_run)
        def wrapper(*args, **kwargs):
            try:
                # Extract prompt from args or kwargs
                prompt = str(args[0]) if args else str(kwargs.get('messages', kwargs.get('input', '')))
                self._recorder.observe_llm(
                    prompt=prompt[:500],
                    response="",
                    metadata={'agent': getattr(agent, 'name', 'openai_agent'), 'method': 'run', 'status': 'started'}
                )
                result = original_run(*args, **kwargs)
                self._recorder.observe_llm(
                    prompt="",
                    response=str(result)[:500],
                    metadata={'agent': getattr(agent, 'name', 'openai_agent'), 'method': 'run', 'status': 'completed'}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'agent': getattr(agent, 'name', 'openai_agent'), 'method': 'run'})
                raise
        return wrapper

    def _wrap_tool(self, original_tool):
        @functools.wraps(original_tool)
        def wrapper(tool_call, **kwargs):
            tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'unknown')
            tool_input = tool_call.get('arguments', '') if isinstance(tool_call, dict) else str(tool_call)
            try:
                result = original_tool(tool_call, **kwargs)
                self._recorder.observe_tool(
                    tool_name=tool_name,
                    input={'arguments': str(tool_input)[:500]},
                    output={'result': str(result)[:500]},
                    metadata={'tool': tool_name}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'tool': tool_name, 'input': str(tool_input)[:200]})
                raise
        return wrapper
