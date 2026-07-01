import sys, json
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
from behavior import BehaviorAnalyzer

# 收集所有已生成的 evidence 文件
evidence_dir = Path("D:/Traccia/tests/integration")
files = list(evidence_dir.glob("*.evidence"))

results = []
for f in files:
    b = BehaviorAnalyzer(str(f))
    results.append(b.report())

print(json.dumps(results, indent=2, ensure_ascii=False))
