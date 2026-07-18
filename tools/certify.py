"""OpenBase Certification Tool"""
import sys, json, hashlib, zipfile
from pathlib import Path
from datetime import datetime, timezone

def certify(evidence_path: str) -> dict:
    path = Path(evidence_path)
    if not path.exists():
        return {"status": "FAIL", "reason": "File not found"}

    with zipfile.ZipFile(evidence_path, "r") as zf:
        required = ["manifest.json", "session.json", "events.jsonl", "signature.sig"]
        missing = [f for f in required if f not in zf.namelist()]
        if missing:
            return {"status": "FAIL", "reason": f"Missing: {missing}"}

        session = json.loads(zf.read("session.json"))
        events_text = zf.read("events.jsonl").decode("utf-8")
        events = [json.loads(l) for l in events_text.strip().split("\n") if l.strip()]

    with open(evidence_path, "rb") as f:
        pkg_hash = hashlib.sha256(f.read()).hexdigest()

    badge_md = "[![OpenBase Certified](https://img.shields.io/badge/OpenBase-Certified-00AA00)](https://github.com/d87skg/OpenBase)"

    return {
        "status": "PASS",
        "package_hash": pkg_hash[:16],
        "session_id": session.get("session_id", ""),
        "objective": session.get("objective", ""),
        "event_count": len(events),
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "badge_markdown": badge_md,
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python certify.py <task.evidence>")
        sys.exit(1)
    result = certify(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
