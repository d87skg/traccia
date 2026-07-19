from .reference.python.session import Session
from .reference.python.event import Event
from .reference.python.evidence import Evidence
from .reference.python.attribution import Attribution
from .reference.python.package import Package


class TracciaSession:

    def __init__(self, objective: str):
        self._session = Session(objective=objective)
        self._events = []
        self._evidences = []
        self._attribution = None
        self._finished = False

    @property
    def session_id(self) -> str:
        return self._session.session_id

    @property
    def objective(self) -> str:
        return self._session.objective

    @property
    def status(self) -> str:
        return self._session.status

    def record(self, event_type: str, payload=None, actor_id: str = 'agent'):
        if self._finished:
            raise RuntimeError('Session 已结束')
        prev_hash = self._events[-1].hash if self._events else None
        event = Event(
            session_id=self._session.session_id,
            event_type=event_type,
            actor_id=actor_id,
            payload=payload or {},
            prev_hash=prev_hash,
        )
        self._events.append(event)
        return event

    def add_evidence(self, event, evidence_type='api_response', sha256_hash='', storage_uri=''):
        evidence = Evidence(
            event_id=event.event_id,
            evidence_type=evidence_type,
            sha256_hash=sha256_hash,
            storage_uri=storage_uri,
        )
        self._evidences.append(evidence)
        return evidence

    def set_attribution(self, executor, supervisor=None, approver=None, policy_id=None):
        self._attribution = Attribution(
            session_id=self._session.session_id,
            executor=executor,
            supervisor=supervisor,
            approver=approver,
            policy_id=policy_id,
        )

    def finish(self):
        self._session.complete()
        self._finished = True

    def fail(self):
        self._session.fail()
        self._finished = True

    def cancel(self):
        self._session.cancel()
        self._finished = True

    def to_package(self):
        if not self._finished:
            raise RuntimeError('请先调用 finish()')
        return Package(
            session=self._session,
            events=self._events,
            evidence_list=self._evidences if self._evidences else None,
            attribution=self._attribution,
        )

    def export(self, filepath: str) -> str:
        package = self.to_package()
        package.save_zip(filepath)
        return filepath

    def __repr__(self):
        return f'TracciaSession({self.session_id[:8]}... | {self.objective[:30]} | {self.status} | {len(self._events)} events)'
