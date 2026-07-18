import sys, json, random
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")

from residual import ResidualCaptureEngine
from recorder import DefaultRecorder
from entropy.injectors import EntropyInjector

def generate_events(recorder, complexity=5, inject_recovery=False):
    """生成包含工具/错误/可选恢复的事件序列。"""
    tools = ["search", "calculate", "read_file", "send_api"]
    for _ in range(complexity):
        tool = random.choice(tools)
        recorder.observe_tool(tool, {"q": "random"}, {"result": "ok"}, {"runtime": "loop"})
        if random.random() < 0.4:  # 40% 概率出错
            recorder.observe_error(ValueError(f"error in {tool}"), {"runtime": "loop"})
            if inject_recovery:
                # 70% 概率恢复
                if random.random() < 0.7:
                    recorder.observe_tool("retry", {"attempt": random.randint(1,3)}, {"result": "recovered"}, {"runtime": "loop"})
    recorder.observe_llm("final_prompt", "final_response", {"runtime": "loop"})

def run_loop(iterations=5, initial_evidence=None):
    if initial_evidence and Path(initial_evidence).exists():
        current_evidence = initial_evidence
    else:
        recorder = DefaultRecorder("Loop Start")
        generate_events(recorder)
        recorder.finish()
        current_evidence = "tests/integration/loop_start.evidence"
        recorder.export(current_evidence)

    history = []
    for i in range(iterations):
        engine = ResidualCaptureEngine(current_evidence)
        residual = engine.extract()
        history.append({"iteration": i, "residual": residual})

        # 根据 recovery 残差决定是否注入恢复行为
        recovery_ratio = residual["recovery"]["recovery_ratio"]
        inject_recovery = recovery_ratio < 0.5  # 如果恢复不足，下一轮注入恢复

        # 根据 semantic 残差调整熵注入参数
        missing = residual["semantic"]["missing_expected"]
        unexpected = residual["semantic"]["unexpected_fields"]
        drift_rate = 0.4 if unexpected else 0.2
        silent_fail_rate = 0.5 if "result_or_data" in missing else 0.2

        injector = EntropyInjector(drift_rate, silent_fail_rate, 0.1)
        recorder = DefaultRecorder(f"Loop Iteration {i}", entropy_injector=injector)
        generate_events(recorder, complexity=random.randint(3,7), inject_recovery=inject_recovery)
        recorder.finish()
        new_evidence = f"tests/integration/loop_iter_{i}.evidence"
        recorder.export(new_evidence)
        current_evidence = new_evidence

        print(f"Iter {i}: recovery_ratio={recovery_ratio:.2f}, inject_recovery={inject_recovery}, "
              f"unexpected={unexpected}, missing={missing}")

    # 保存历史
    corpus_dir = Path("D:/Traccia/registry/corpus")
    corpus_dir.mkdir(parents=True, exist_ok=True)
    with open(corpus_dir / "loop_history.jsonl", "a") as f:
        for entry in history:
            f.write(json.dumps(entry) + "\n")
    print(f"Loop complete. History saved.")
    return history