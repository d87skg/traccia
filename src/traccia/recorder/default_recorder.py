import sys
from pathlib import Path
from typing import Any, Dict, Optional

# 确保 reference 包在路径中
_reference_path = Path('D:/Traccia/traccia/reference')
if str(_reference_path) not in sys.path:
    sys.path.insert(0, str(_reference_path))

from python.session import Session
from python.event import Event
from python.evidence import Evidence
from python.package import Package

from .recorder import Recorder
from .mapper import CanonicalMapper, SimplePassThroughMapper

# 引入熵注入器
_entropy_path = Path('D:/Traccia/src/traccia')
if str(_entropy_path) not in sys.path:
    sys.path.insert(0, str(_entropy_path))
# entropy moved to labs

class DefaultRecorder(Recorder):
    def __init__(self, objective: str = "Default Session", 
                 mapper: Optional[CanonicalMapper] = None,
                 entropy_injector=None):
        self._session = Session(objective=objective)
        self._events = []
        self._evidences = []
        self._finished = False
        self._mapper = mapper or SimplePassThroughMapper()
        self._entropy_injector = entropy_injector

    def observe_llm(self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        payload = {"prompt": prompt, "response": response}
        if metadata:
            payload.update(metadata)
        return self._record_event("llm_call", payload)

    def observe_tool(self, tool_name: str, input: Dict[str, Any], output: Dict[str, Any],
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        # 注入熵：修改输出以产生语义残差
        modified_output = self._entropy_injector.inject(output)
        
        payload = {"tool": tool_name, "input": input, "output": modified_output}
        if metadata:
            payload.update(metadata)
        return self._record_event("tool_call", payload)

    def observe_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        payload = {"error": str(error), "type": type(error).__name__}
        if context:
            payload["context"] = context
        return self._record_event("error", payload)

    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        if self._finished:
            raise RuntimeError("Session already finished")
        prev_hash = self._events[-1].hash if self._events else None

        # Canonical mapping
        raw_event = {"event_type": event_type, "payload": payload}
        canonical_type, canonical_payload = self._mapper.map(raw_event)

        # 存储原始事件和规范化类型
        enriched_payload = {
            **payload,
            "_canonical_type": canonical_type,
            "_canonical_payload": canonical_payload
        }

        event = Event(
            session_id=self._session.session_id,
            event_type=event_type,
            actor_id="agent",
            payload=enriched_payload,
            prev_hash=prev_hash,
        )
        self._events.append(event)
        return event.event_id

    def finish(self) -> str:
        self._session.complete()
        self._finished = True
        return self._session.session_id

    def export(self, filepath: str) -> str:
        if not self._finished:
            self.finish()
        package = Package(
            session=self._session,
            events=self._events,
            evidence_list=self._evidences,
        )
        package.save_zip(filepath)
        return filepath