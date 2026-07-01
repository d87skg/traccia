import sys
from pathlib import Path
from typing import Optional, Dict, Any
import functools

_src_path = Path('D:/Traccia/src/traccia')
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class LangChainEmitter:
    """Emitter for LangChain. Monkey-patches AgentExecutor or Runnable to record events."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch(self, executor):
        # Patch common interfaces: invoke (LangChain 1.3+), run (legacy), _call (internal)
        if hasattr(executor, 'invoke'):
            original_invoke = executor.invoke
            executor.invoke = self._wrap_invoke(original_invoke)
        if hasattr(executor, 'run'):
            original_run = executor.run
            executor.run = self._wrap_run(original_run)
        if hasattr(executor, '_call'):
            original_call = executor._call
            executor._call = self._wrap_call(original_call)
        return executor

    def _wrap_invoke(self, original_invoke):
        @functools.wraps(original_invoke)
        def wrapper(inputs, *args, **kwargs):
            try:
                self._recorder.observe_llm(
                    prompt=str(inputs),
                    response="",
                    metadata={'method': 'invoke', 'status': 'started'}
                )
                result = original_invoke(inputs, *args, **kwargs)
                self._recorder.observe_llm(
                    prompt="",
                    response=str(result),
                    metadata={'method': 'invoke', 'status': 'completed'}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'method': 'invoke', 'inputs': str(inputs)})
                raise
        return wrapper

    def _wrap_run(self, original_run):
        @functools.wraps(original_run)
        def wrapper(*args, **kwargs):
            try:
                result = original_run(*args, **kwargs)
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'action': 'agent_executor.run'})
                raise
        return wrapper

    def _wrap_call(self, original_call):
        @functools.wraps(original_call)
        def wrapper(inputs, *args, **kwargs):
            try:
                result = original_call(inputs, *args, **kwargs)
                self._recorder.observe_llm(
                    prompt=str(inputs),
                    response=str(result),
                    metadata={'method': '_call'}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {'inputs': str(inputs)})
                raise
        return wrapper
