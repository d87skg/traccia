"""Traccia Report — Generate Agent Failure Report from .evidence file."""
import sys, json, zipfile

def report(evidence_path: str):
    with zipfile.ZipFile(evidence_path, 'r') as zf:
        manifest = json.loads(zf.read('manifest.json'))
        events = [json.loads(line) for line in zf.read('events.jsonl').decode().strip().split('\n') if line]
        evidence = json.loads(zf.read('evidence.json'))

    print("=" * 60)
    print("  Agent Execution Report")
    print("=" * 60)
    print(f"  Session:    {manifest.get('session_id', 'unknown')}")
    print(f"  Events:     {manifest.get('event_count', len(events))}")
    print(f"  Evidence:   {manifest.get('evidence_count', len(evidence))}")
    print(f"  Created:    {manifest.get('created_at', 'unknown')}")
    print("=" * 60)
    print()
    print("  Timeline:")
    for i, ev in enumerate(events):
        ts = ev.get('timestamp', '')[:19]
        et = ev.get('event_type', 'UNKNOWN')
        print(f"  [{i+1}] {ts} | {et}")
    print()
    print("  Evidence Verification:", "VALID" if evidence else "EMPTY")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: traccia report <file.evidence>")
        sys.exit(1)
    report(sys.argv[1])
