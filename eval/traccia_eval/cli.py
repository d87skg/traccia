import json, sys
from pathlib import Path

def main():
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "D:/Traccia/dataset/traccia_benchmark.jsonl"
    with open(dataset_path, encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    from traccia_eval.scorer import traccia_score
    for entry in entries:
        entry["evaluation"]["final_score"] = traccia_score(entry)

    ranked = sorted(entries, key=lambda x: x["evaluation"]["final_score"], reverse=True)
    print("Rank | Score | Entry")
    for i, e in enumerate(ranked, 1):
        print(f"{i:<4} | {e['evaluation']['final_score']:.4f} | {e['id']}")
