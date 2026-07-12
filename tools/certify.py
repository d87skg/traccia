"""Traccia Certification — wraps OpenBase Core Verifier for convenience."""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path("D:/openbase").absolute()))
from conformance.certify import certify as openbase_certify

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python certify.py <task.evidence>")
        sys.exit(1)
    result = openbase_certify(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
