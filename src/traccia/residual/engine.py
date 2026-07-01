import zipfile, json
from pathlib import Path
from typing import Dict, Any, List

class ResidualCaptureEngine:
    def __init__(self, evidence_path: str):
        self.path = Path(evidence_path)
        self.events = self._load_events()

    def _load_events(self) -> List[Dict]:
        if not self.path.exists():
            return []
        with zipfile.ZipFile(self.path, 'r') as zf:
            if 'events.jsonl' in zf.namelist():
                content = zf.read('events.jsonl').decode('utf-8').strip()
                return [json.loads(line) for line in content.split(chr(10)) if line.strip()]
        return []

    def extract(self) -> Dict[str, Any]:
        return {
            "temporal": self._temporal_residual(),
            "semantic": self._semantic_residual(),
            "structural": self._structural_residual(),
            "recovery": self._recovery_residual(),
        }

    def _temporal_residual(self) -> Dict:
        timestamps = [ev.get("timestamp", "") for ev in self.events if ev.get("timestamp")]
        dup_ts = len(timestamps) - len(set(timestamps))
        return {
            "event_count": len(self.events),
            "duplicate_timestamps": dup_ts,
            "note": "Temporal clustering or duplicate timestamps may indicate batching/latency issues."
        }

    def _semantic_residual(self) -> Dict:
        expected_keys = {"tool", "input", "output", "result", "status", "data", "error"}
        unexpected_fields = []
        missing_expected = []
        for ev in self.events:
            payload = ev.get("payload", {})
            if not isinstance(payload, dict):
                continue
            output = payload.get("output", {})
            if isinstance(output, dict):
                for key in output.keys():
                    if key not in expected_keys and not key.startswith("_"):
                        unexpected_fields.append(key)
                if "result" not in output and "data" not in output:
                    missing_expected.append("result_or_data")
            for key in expected_keys:
                if key in payload and payload[key] is None:
                    missing_expected.append(key)
        return {
            "unexpected_fields": list(set(unexpected_fields)),
            "missing_expected": list(set(missing_expected)),
            "note": "Semantic residuals detected if unexpected fields appear or expected fields are missing."
        }

    def _structural_residual(self) -> Dict:
        chain_breaks = 0
        for i, ev in enumerate(self.events):
            if i == 0:
                continue
            expected_prev = self.events[i-1].get("hash", "")
            actual_prev = ev.get("prev_hash", "")
            if actual_prev and actual_prev != expected_prev:
                chain_breaks += 1
        return {
            "chain_breaks": chain_breaks,
            "note": "Hash chain integrity issues indicate structural anomalies."
        }

    def _recovery_residual(self) -> Dict:
        error_events = [ev for ev in self.events if ev.get("event_type") == "error"]
        recovery_events = [ev for ev in self.events if "retry" in str(ev.get("payload", "")).lower() or "replan" in str(ev.get("payload", "")).lower()]
        return {
            "error_count": len(error_events),
            "recovery_attempts": len(recovery_events),
            "recovery_ratio": len(recovery_events) / max(1, len(error_events)),
            "note": "Recovery gap indicates the system did not attempt to mitigate failures."
        }
