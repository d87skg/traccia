import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path(__file__).parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class AutoGenEmitter:
    """Emitter for AutoGen. Monkey-patches ConversableAgent to record LLM and tool events."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, agent):
        """Patch an AutoGen agent instance."""
        if hasattr(agent, 'generate_reply'):
            original_reply = agent.generate_reply
            agent.generate_reply = self._wrap_reply(original_reply, agent)

        if hasattr(agent, 'execute_tool'):
            original_tool = agent.execute_tool
            agent.execute_tool = self._wrap_tool(original_tool)

        # Also register nested agents for group chat
        if hasattr(agent, 'register_nested_chats'):
            original_register = agent.register_nested_chats
            agent.register_nested_chats = self._wrap_register(original_register)

        return agent

    def _wrap_reply(self, original_reply, agent):
        @functools.wraps(original_reply)
        def wrapper(messages=None, sender=None, config=None, **kwargs):
            try:
                self._recorder.observe_llm(
                    prompt=str(messages)[:500],
                    response="",
                    metadata={'agent': agent.name if hasattr(agent, 'name') else 'unknown', 'method': 'generate_reply', 'status': 'started'}
                )
                reply = original_reply(messages=messages, sender=sender, config=config, **kwargs)
                self._recorder.observe_llm(
                    prompt="",
                    response=str(reply)[:500],
                    metadata={'agent': agent.name if hasattr(agent, 'name') else 'unknown', 'method': 'generate_reply', 'status': 'completed'}
                )
                return reply
            except Exception as e:
                self._recorder.observe_error(e, {'agent': agent.name if hasattr(agent, 'name') else 'unknown', 'method': 'generate_reply'})
                raise
        return wrapper

    def _wrap_tool(self, original_tool):
        @functools.wraps(original_tool)
        def wrapper(tool_call, **kwargs):
            tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else 'unknown'
            input = tool_call.get('arguments', '') if isinstance(tool_call, dict) else str(tool_call)
            try:
                result = original_tool(tool_call, **kwargs)
                self._recorder.observe_tool(
                    tool_name=tool_name,
                    input={'arguments': input},
                    output={'result': str(result)[:500]},
                    metadata={'tool': tool_name}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'tool': tool_name, 'input': str(input)})
                raise
        return wrapper

    def _wrap_register(self, original_register):
        @functools.wraps(original_register)
        def wrapper(nested_chats, **kwargs):
            # Patch any nested agents
            for chat in nested_chats:
                for agent in chat.get('agents', []):
                    self.patch(agent)
            return original_register(nested_chats, **kwargs)
        return wrapper
