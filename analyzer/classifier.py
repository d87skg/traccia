import json, zipfile
from pathlib import Path

ERROR_PATTERNS = {
    "tool_timeout": {"keywords": ["timeout", "timed out", "deadline exceeded"], "category": "tool_error"},
    "api_rate_limit": {"keywords": ["rate limit", "429", "too many requests", "quota exceeded"], "category": "tool_error"},
    "tool_not_found": {"keywords": ["tool not found", "no such tool"], "category": "tool_error"},
    "empty_response": {"keywords": ["empty response", "null result"], "category": "tool_error"},
    "missing_parameter": {"keywords": ["missing", "required", "parameter"], "category": "prompt_error"},
    "model_refusal": {"keywords": ["I cannot", "I apologize", "unable to"], "category": "model_error"},
    "network_error": {"keywords": ["connection refused", "network", "unreachable"], "category": "environment_error"},
    "permission_denied": {"keywords": ["permission denied", "access denied", "forbidden", "403"], "category": "environment_error"}
}

def classify_error(text: str):
    matches = []
    text_lower = text.lower()
    for pattern_name, pattern in ERROR_PATTERNS.items():
        for keyword in pattern["keywords"]:
            if keyword.lower() in text_lower:
                matches.append({"pattern": pattern_name, "category": pattern["category"], "matched_keyword": keyword})
                break
    return matches

def extract_errors_from_package(package_path: str):
    if not Path(package_path).exists():
        return []
    errors = []
    with zipfile.ZipFile(package_path, "r") as zf:
        if "events.jsonl" in zf.namelist():
            content = zf.read("events.jsonl").decode("utf-8")
            for line in content.strip().split("\n"):
                if not line.strip(): continue
                event = json.loads(line)
                payload_str = json.dumps(event.get("payload", {})).lower()
                matches = classify_error(payload_str)
                if not matches:
                    matches = classify_error(event.get("event_type", ""))
                if matches:
                    errors.append({"event_id": event.get("event_id", ""), "event_type": event.get("event_type", ""), "timestamp": event.get("timestamp", ""), "matches": matches})
    return errors
