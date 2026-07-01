import sys, json, zipfile
from pathlib import Path

sys.path.insert(0, "D:/Traccia/src/traccia")
sys.path.insert(0, "D:/Traccia/traccia/reference")
from residual import ResidualCaptureEngine

def build_canonical_entry(evidence_path, task_id=None):
    """将 evidence 包转换为 Canonical Schema v1 条目"""
    engine = ResidualCaptureEngine(str(evidence_path))
    residual = engine.extract()
    
    # 提取事件作为 trajectory
    trajectory = []
    for ev in engine.events:
        trajectory.append({
            "step": len(trajectory) + 1,
            "type": ev.get("event_type", "unknown"),
            "input": str(ev.get("payload", {}).get("input", "")),
            "output": str(ev.get("payload", {}).get("output", "")),
            "status": "error" if ev.get("event_type") == "error" else "success",
            "latency": 0,
            "metadata": ev.get("payload", {})
        })
    
    # 计算评估分数
    recovery = residual["recovery"]
    semantic = residual["semantic"]
    structural = residual["structural"]
    
    correctness = 0.0 if recovery["error_count"] > 0 else 1.0
    stability = 1.0 if structural["chain_breaks"] == 0 else 0.5
    recoverability = recovery["recovery_ratio"]
    entropy = 0.5 if semantic["unexpected_fields"] else 0.2
    efficiency = 1.0 if len(engine.events) < 10 else 0.7
    
    final_score = (
        0.3 * correctness +
        0.2 * stability +
        0.2 * recoverability +
        0.2 * (1 - entropy) +
        0.1 * efficiency
    )
    
    return {
        "id": f"entry_{task_id or evidence_path.stem}",
        "task": {
            "task_id": task_id or evidence_path.stem,
            "instruction": f"Execution task from {evidence_path.name}",
            "goal": "complete execution",
            "difficulty": 0.5,
            "domain": "tool-use"
        },
        "execution": {
            "runtime": "stg-loop",
            "mode": "tool",
            "steps": len(engine.events),
            "success": correctness > 0
        },
        "trajectory": trajectory,
        "residual": {
            "temporal_residual": residual["temporal"]["duplicate_timestamps"] / max(1, len(engine.events)),
            "semantic_residual": 0.5 if semantic["unexpected_fields"] else 0.1,
            "structural_residual": 0.3 if structural["chain_breaks"] > 0 else 0.0,
            "recovery_residual": 1 - recoverability,
            "entropy": entropy,
            "drift_detected": len(semantic["unexpected_fields"]) > 0,
            "anomalies": semantic["unexpected_fields"] + semantic["missing_expected"]
        },
        "evaluation": {
            "correctness": correctness,
            "failure_type": ["silent_failure"] if correctness == 0 else [],
            "recoverability": recoverability,
            "efficiency_score": efficiency,
            "stability_score": stability,
            "final_score": round(final_score, 4)
        },
        "meta": {
            "schema_version": "1.0",
            "generator": "traccia-dataset-builder-v0.1",
            "source": "synthetic",
            "license": "apache-2.0",
            "tags": ["agent", "execution", "residual-analysis"]
        }
    }

if __name__ == "__main__":
    # 收集所有 evidence 文件（包括 loop 生成的）
    evidence_files = list(Path("D:/Traccia/tests/integration").glob("*.evidence"))
    evidence_files += list(Path("D:/Traccia/evidence").glob("*.evidence"))
    evidence_files += list(Path("D:/Traccia/tests/integration").glob("loop_iter_*.evidence"))
    
    dataset = []
    for i, f in enumerate(evidence_files):
        entry = build_canonical_entry(f, f"task_{i:03d}")
        dataset.append(entry)
        print(f"Processed: {f.name}")
    
    # 保存为 JSONL
    output_file = "D:/Traccia/dataset/traccia_benchmark.jsonl"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"Dataset exported: {output_file} ({len(dataset)} entries)")
