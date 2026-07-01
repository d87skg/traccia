import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path('D:/Traccia/src/traccia')
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class CrewAIEmitter:
    """Emitter for CrewAI. Monkey-patches Crew/Agent/Tool to record events."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, crew):
        """Patch a Crew instance and its agents/tools."""
        # Patch crew kickoff
        original_kickoff = crew.kickoff
        crew.kickoff = self._wrap_kickoff(original_kickoff)

        # Patch agents and their tools
        for agent in getattr(crew, 'agents', []):
            self._patch_agent(agent)

    def _patch_agent(self, agent):
        # Patch agent's execute_task
        if hasattr(agent, 'execute_task'):
            original_exec = agent.execute_task
            agent.execute_task = self._wrap_execute_task(original_exec, agent)
        # Patch tools
        for tool in getattr(agent, 'tools', []):
            self._patch_tool(tool)

    def _patch_tool(self, tool):
        if hasattr(tool, 'run'):
            original_run = tool.run
            tool.run = self._wrap_tool_run(original_run, tool)

    def _wrap_kickoff(self, original_kickoff):
        @functools.wraps(original_kickoff)
        def wrapper(*args, **kwargs):
            try:
                result = original_kickoff(*args, **kwargs)
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'action': 'crew.kickoff'})
                raise
        return wrapper

    def _wrap_execute_task(self, original_exec, agent):
        @functools.wraps(original_exec)
        def wrapper(task, *args, **kwargs):
            # Record agent task start
            self._recorder.observe_llm(
                prompt=f"Agent {agent.role} executing task: {task}",
                response="",
                metadata={'agent_role': agent.role, 'task': str(task)}
            )
            try:
                result = original_exec(task, *args, **kwargs)
                # Record success
                self._recorder.observe_llm(
                    prompt="",
                    response=str(result),
                    metadata={'agent_role': agent.role, 'task': str(task)}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'agent_role': agent.role, 'task': str(task)})
                raise
        return wrapper

    def _wrap_tool_run(self, original_run, tool):
        @functools.wraps(original_run)
        def wrapper(*args, **kwargs):
            input_arg = args[0] if args else kwargs
            try:
                output = original_run(*args, **kwargs)
                self._recorder.observe_tool(
                    tool_name=tool.name,
                    input={'args': input_arg},
                    output={'result': str(output)},
                    metadata={'tool_name': tool.name}
                )
                return output
            except Exception as e:
                self._recorder.observe_error(e, {'tool_name': tool.name, 'input': str(input_arg)})
                raise
        return wrapper
