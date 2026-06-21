from .rules import evaluate, BlockedActionError

class GuardSession:
    def __init__(self, objective: str):
        self.objective = objective
        self.events = []
        self.warnings = []
        self._finished = False

    def record(self, event_type: str, payload: dict = None):
        if self._finished:
            raise RuntimeError("Session 已结束")

        action, msg = evaluate(payload or {})
        if action == "BLOCK":
            raise BlockedActionError(msg)
        if action == "WARN":
            self.warnings.append(msg)

        event = {
            "event_type": event_type,
            "payload": payload or {},
            "status": "ALLOW" if action == "ALLOW" else action
        }
        self.events.append(event)
        return event

    def finish(self):
        self._finished = True

    def to_dict(self):
        return {
            "objective": self.objective,
            "events": self.events,
            "warnings": self.warnings
        }
