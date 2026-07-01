import sys
from pathlib import Path
import time

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")

from recorder import DefaultRecorder

def generate_task(output_path: str):
    recorder = DefaultRecorder("STG Task: Temporal Clustering & Recovery")

    # 诱发 temporal 残差：快速连续调用
    for i in range(10):
        recorder.observe_tool("fast_tool", {"step": i}, {"result": "ok"}, {"runtime": "stg"})

    # 诱发 recovery 残差
    recorder.observe_error(ValueError("Temporary failure"), {"runtime": "stg"})
    recorder.observe_tool("retry", {"attempt": 1}, {"result": "recovered"}, {"runtime": "stg"})
    recorder.observe_error(ValueError("Second failure"), {"runtime": "stg"})
    # 故意不 retry

    recorder.finish()
    path = recorder.export(output_path)
    print("Generated:", path)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "tests/integration/stg_generated_task.evidence"
    generate_task(out)
