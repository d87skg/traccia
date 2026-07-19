import sys, json, zipfile, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia_sdk import start

def load_events(path):
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events

def load_evidence_map(path):
    emap = {}
    with zipfile.ZipFile(path, "r") as zf:
        for name in zf.namelist():
            parts = name.replace("\\", "/").split("/")
            event_id = "unknown"
            for part in parts:
                if part.startswith("event_"):
                    event_id = part.split("_")[1] if "_" in part else "unknown"
                    break
            emap.setdefault(event_id, []).append(name)
    return emap

def convert(events_jsonl, evidence_zip, output):
    events = load_events(events_jsonl)
    emap = load_evidence_map(evidence_zip) if evidence_zip else {}
    if not events:
        print("Error: no events")
        sys.exit(1)

    obj = events[0].get("case_id", events[0].get("session", "Blackbox"))
    session = start(objective=f"Blackbox: {obj}")

    for ev in events:
        etype = ev.get("event_type", ev.get("type", "unknown"))
        actor = ev.get("actor", ev.get("app", "blackbox"))
        payload = ev.get("payload", ev.get("detail", {}))
        if not isinstance(payload, dict):
            payload = {"raw": str(payload)}

        e = session.record(event_type=etype, payload=payload, actor_id=actor)

        eid = ev.get("event_id", "")
        for f in emap.get(eid, []):
            session.add_evidence(e, evidence_type="screenshot" if ".png" in f else "log_snapshot",
                                 sha256_hash=ev.get("hash", ""), storage_uri=f"blackbox://{f}")

    session.finish()
    path = session.export(output)

    from traccia_sdk.reference.python.validator import verify
    result = verify(path)
    print(f"Session: {session.session_id[:12]}...")
    print(f"Events:  {len(events)}")
    print(f"Evidence:{sum(len(v) for v in emap.values())} files")
    print(f"Output:  {path}")
    print(f"Verify:  {result.status}")
    if not result.is_valid:
        print(result.report())
        sys.exit(1)
    return path

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Blackbox -> Traccia converter")
    p.add_argument("events_jsonl")
    p.add_argument("evidence_zip", nargs="?")
    p.add_argument("--output", "-o", default="task.evidence")
    args = p.parse_args()
    convert(args.events_jsonl, args.evidence_zip, args.output)
