import sys, json
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
from residual import ResidualCaptureEngine

evidence_files = list(Path("D:/Traccia/tests/integration").glob("diversity_*.evidence"))

report = {}
for f in evidence_files:
    engine = ResidualCaptureEngine(str(f))
    report[f.name] = engine.extract()

print(json.dumps(report, indent=2, ensure_ascii=False))
