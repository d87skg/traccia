import json, sys
from pathlib import Path

def load_dataset(filepath):
    entries = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def generate_leaderboard(dataset_path):
    data = load_dataset(dataset_path)
    
    # 提取评分并排序
    ranked = sorted(data, key=lambda x: x["evaluation"]["final_score"], reverse=True)
    
    print("=" * 70)
    print("T R A C C I A   A G E N T   E X E C U T I O N   L E A D E R B O A R D")
    print("=" * 70)
    print(f"{'Rank':<6}{'Entry':<25}{'Score':<10}{'Recovery':<12}{'Stability':<10}{'Runtime':<15}")
    print("-" * 70)
    
    for rank, entry in enumerate(ranked, 1):
        ev = entry["evaluation"]
        ex = entry["execution"]
        print(f"{rank:<6}{entry['id'][:24]:<25}{ev['final_score']:<10.4f}{ev['recoverability']:<12.2f}{ev['stability_score']:<10.2f}{ex['runtime']:<15}")
    
    print("=" * 70)
    print(f"Total entries: {len(ranked)}")
    
    # 保存排名到文件
    leaderboard = []
    for rank, entry in enumerate(ranked, 1):
        leaderboard.append({
            "rank": rank,
            "id": entry["id"],
            "runtime": entry["execution"]["runtime"],
            "score": entry["evaluation"]["final_score"],
            "recoverability": entry["evaluation"]["recoverability"],
            "stability": entry["evaluation"]["stability_score"],
            "correctness": entry["evaluation"]["correctness"],
        })
    
    output = "D:/Traccia/dataset/leaderboard.json"
    with open(output, "w") as f:
        json.dump(leaderboard, f, indent=2)
    print(f"Leaderboard saved: {output}")

if __name__ == "__main__":
    generate_leaderboard("D:/Traccia/dataset/traccia_benchmark.jsonl")
