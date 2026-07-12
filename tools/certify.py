"""OpenBase Compatible Badge — verify an evidence package and output certification."""

import sys, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia.reference.python.validator import verify

def certify(evidence_path: str) -> dict:
    """Verify evidence and return certification result."""
    path = Path(evidence_path)
    if not path.exists():
        return {"status": "FAIL", "reason": "File not found"}

    # Step 1: Verify integrity
    result = verify(evidence_path)
    if not result.is_valid:
        return {"status": "FAIL", "reason": "Evidence verification failed", "details": result.report()}

    # Step 2: Check required components
    import zipfile
    required_files = ["session.json", "events.jsonl", "signature.sig"]
    with zipfile.ZipFile(evidence_path, "r") as zf:
        missing = [f for f in required_files if f not in zf.namelist()]
        if missing:
            return {"status": "FAIL", "reason": f"Missing required files: {missing}"}

        # Step 3: Extract metadata
        session = json.loads(zf.read("session.json"))
        events_text = zf.read("events.jsonl").decode("utf-8")
        event_count = len([l for l in events_text.strip().split("\n") if l.strip()])

    # Step 4: Compute package hash
    with open(evidence_path, "rb") as f:
        pkg_hash = hashlib.sha256(f.read()).hexdigest()

    # Step 5: Generate badge
    badge_url = "https://img.shields.io/badge/OpenBase-Compatible-00AA00?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik05IDE2LjE3TDQuODMgMTJsLTEuNDIgMS40MUw5IDE5IDIxIDdsLTEuNDEtMS40MXoiLz48L3N2Zz4="
    badge_markdown = f"[![OpenBase Compatible]({badge_url})](https://github.com/d87skg/traccia)"

    return {
        "status": "PASS",
        "package_hash": pkg_hash[:16],
        "session_id": session.get("session_id", ""),
        "objective": session.get("objective", ""),
        "event_count": event_count,
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "badge_markdown": badge_markdown,
        "badge_html": f'<img src="{badge_url}" alt="OpenBase Compatible">',
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python certify.py <task.evidence>")
        print("")
        print("Example:")
        print("  python tools/certify.py evidence/my_agent.evidence")
        sys.exit(1)

    result = certify(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("")
    if result["status"] == "PASS":
        print("✅ OpenBase Compatible Certified!")
        print("")
        print("Add this badge to your README:")
        print(result["badge_markdown"])
