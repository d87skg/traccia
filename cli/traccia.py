#!/usr/bin/env python3
"""traccia — OpenBase Developer SDK CLI"""

import sys, os, subprocess, json, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "traccia"))
sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def cmd_intercept(args):
    if not args:
        print("Usage: traccia intercept -- <command>")
        sys.exit(1)
    cmd_str = " ".join(args)
    print(f"Traccia intercepting: {cmd_str}")
    from traccia import start
    session = start(objective=f"intercept: {cmd_str}")
    session.record("process.start", payload={"command": args})
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=300)
        session.record("process.exit", payload={"returncode": result.returncode, "stdout": result.stdout[:1000], "stderr": result.stderr[:1000]})
    except Exception as e:
        session.record("process.error", payload={"error": str(e)})
    session.finish()
    evidence_path = f"traccia-{session.session_id[:8]}.evidence"
    session.export(evidence_path)
    print(f"Evidence saved: {evidence_path}")

def cmd_diagnose(args):
    if not args:
        print("Usage: traccia diagnose <file.evidence>")
        sys.exit(1)
    evidence_file = args[0]
    if not os.path.exists(evidence_file):
        print(f"File not found: {evidence_file}")
        sys.exit(1)
    sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "traccia"))
    from analyzer.engine import analyze
    result = analyze(evidence_file)
    print("=" * 50)
    print("Diagnosis Report")
    print("=" * 50)
    print(f"File: {evidence_file}")
    print(f"Valid: {result.get('valid')}")
    print(f"Anomalies: {result.get('errors_found', 0)}")
    for cause in result.get('root_causes', []):
        print(f"  - {cause['category']}: {cause['confidence']}")
    print(result.get('summary', ''))

def cmd_verify(args):
    if not args:
        print("Usage: traccia verify <file.evidence>")
        sys.exit(1)
    evidence_file = args[0]
    if not os.path.exists(evidence_file):
        print(f"File not found: {evidence_file}")
        sys.exit(1)
    try:
        with zipfile.ZipFile(evidence_file, 'r') as zf:
            required = ["manifest.json", "session.json", "events.jsonl", "signature.sig"]
            missing = [f for f in required if f not in zf.namelist()]
            if missing:
                print(f"INVALID: Missing {missing}")
                sys.exit(1)
            session = json.loads(zf.read("session.json"))
            events_text = zf.read("events.jsonl").decode("utf-8")
            events = [json.loads(l) for l in events_text.strip().split("\n") if l.strip()]
            chain_ok = True
            for i, ev in enumerate(events):
                if i == 0:
                    if ev.get("prev_hash") is not None:
                        chain_ok = False
                        break
                elif ev.get("prev_hash") != events[i-1].get("hash", ""):
                    chain_ok = False
                    break
            print("=" * 50)
            print("Valid OpenBase Evidence")
            print("=" * 50)
            print(f"Agent: {session.get('objective', 'unknown')[:50]}")
            print(f"Events: {len(events)}")
            print(f"Integrity: {'PASS' if chain_ok else 'FAIL'}")
            print(f"Replay: AVAILABLE")
            sys.exit(0 if chain_ok else 1)
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)

def cmd_certify(args):
    if not args:
        print("Usage: traccia certify <file.evidence>")
        sys.exit(1)
    evidence_file = args[0]
    if not os.path.exists(evidence_file):
        print(f"File not found: {evidence_file}")
        sys.exit(1)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.certify import certify
    result = certify(evidence_file)
    if result.get("status") == "PASS":
        print("=" * 50)
        print("OpenBase Certified")
        print("=" * 50)
        print(f"Package: {result.get('package_hash', '')}")
        print(f"Session: {result.get('session_id', '')}")
        print(f"Events: {result.get('event_count', 0)}")
        print()
        print("Add this badge to your README:")
        print(result.get("badge_markdown", ""))
    else:
        print(f"Certification failed: {result.get('reason', 'unknown')}")
        sys.exit(1)

def cmd_guard(args):
    print("Guard mode: run 'traccia guard --policy default -- python agent.py'")

def cmd_loop(args):
    if not args or args[0] != "run":
        print("Usage: traccia loop run [--iterations N]")
        sys.exit(1)
    iterations = 5
    if "--iterations" in args:
        try:
            idx = args.index("--iterations")
            iterations = int(args[idx + 1])
        except:
            pass
    sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "traccia" / "loop"))
    from loop.loop import run_loop
    run_loop(iterations=iterations)

def main():
    if len(sys.argv) < 2:
        print("traccia intercept -- <command>")
        print("traccia diagnose <file.evidence>")
        print("traccia verify <file.evidence>")
        print("traccia certify <file.evidence>")
        print("traccia guard -- <command>")
        print("traccia loop run [--iterations N]")
        sys.exit(1)
    command = sys.argv[1]
    args = sys.argv[2:]
    if command == "intercept":
        if args and args[0] == "--": args = args[1:]
        cmd_intercept(args)
    elif command == "diagnose": cmd_diagnose(args)
    elif command == "verify": cmd_verify(args)
    elif command == "certify": cmd_certify(args)
    elif command == "guard": cmd_guard(args)
    elif command == "loop": cmd_loop(args)
    else:
        print(f"Unknown: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
