
import time, random, sys
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")

from recorder import DefaultRecorder

recorder = DefaultRecorder("STG Task: Temporal Clustering & Recovery")

# 快速连续调用工具（诱发 temporal 残差）
for i in range(10):
    recorder.observe_tool("fast_tool", {"step": i}, {"result": "ok"}, {"runtime": "stg"})
    time.sleep(0.01)  # 极小延迟，导致时间戳可能重复

# 模拟可恢复错误（诱发 recovery 残差）
recorder.observe_error(ValueError("Temporary failure"), {"runtime": "stg"})
recorder.observe_tool("retry", {"attempt": 1}, {"result": "recovered"}, {"runtime": "stg"})
recorder.observe_error(ValueError("Second failure"), {"runtime": "stg"})
# 故意不 retry，制造 recovery 缺失

recorder.finish()
path = recorder.export("tests/integration/stg_generated_task.evidence")
print("Generated:", path)
