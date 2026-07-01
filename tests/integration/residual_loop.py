import sys, json, subprocess
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
from residual import ResidualCaptureEngine

# 1. 分析上一轮生成的证据包
prev_evidence = "tests/integration/stg_with_entropy.evidence"
engine = ResidualCaptureEngine(prev_evidence)
residual = engine.extract()

print("当前残差:")
print(json.dumps(residual, indent=2))

# 2. 根据残差动态调整熵注入参数
missing = residual["semantic"]["missing_expected"]
unexpected = residual["semantic"]["unexpected_fields"]

# 如果发现 missing_expected，增加 silent_fail 概率
# 如果发现 unexpected_fields，增加 schema_drift 概率
drift_rate = 0.3
silent_fail_rate = 0.3
corrupt_rate = 0.2

if "result_or_data" in missing:
    silent_fail_rate = 0.6  # 更积极地制造静默失败
if "confidence" in unexpected or "unexpected_field" in unexpected:
    drift_rate = 0.6  # 更积极地制造字段漂移

print(f"调整后注入参数: drift={drift_rate}, silent={silent_fail_rate}, corrupt={corrupt_rate}")

# 3. 用调整后的参数生成新任务（通过修改 DefaultRecorder 的注入器参数）
# 这里直接生成一个新的 evidence 包，模拟调整后的行为
from recorder import DefaultRecorder

# 临时修改注入器参数（通过 monkey-patch 熵注入器的初始化参数）
import entropy.injectors
original_init = entropy.injectors.EntropyInjector.__init__
def patched_init(self, drift_rate=drift_rate, silent_fail_rate=silent_fail_rate, corrupt_rate=corrupt_rate):
    original_init(self, drift_rate, silent_fail_rate, corrupt_rate)
entropy.injectors.EntropyInjector.__init__ = patched_init

recorder = DefaultRecorder("Residual Loop Task")
# 模拟正常操作与故障
recorder.observe_llm("Hello", "Hi", {"runtime": "loop"})
recorder.observe_tool("search", {"q": "test"}, {"result": "found"}, {"runtime": "loop"})
recorder.observe_error(ValueError("Something went wrong"), {"runtime": "loop"})
recorder.observe_tool("retry", {"attempt": 1}, {"result": "recovered"}, {"runtime": "loop"})
recorder.finish()
new_path = recorder.export("tests/integration/loop_adjusted.evidence")
print(f"新证据包: {new_path}")

# 4. 分析新证据包
engine2 = ResidualCaptureEngine(new_path)
new_residual = engine2.extract()
print("\n调整后残差:")
print(json.dumps(new_residual, indent=2))
