import sys, json, hashlib, os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia_sdk.reference.python.validator import verify

REGISTRY_DIR = Path("D:/Traccia/registry")
REGISTRY_FILE = REGISTRY_DIR / "entries.jsonl"

def register(package_path):
    if not Path(package_path).exists():
        print(f"Error: file not found: {package_path}")
        return

    # 验证
    result = verify(package_path)
    if not result.is_valid:
        print(f"Verify FAILED: {package_path}")
        return

    # 计算包哈希
    with open(package_path, "rb") as f:
        pkg_hash = hashlib.sha256(f.read()).hexdigest()

    # 生成 evidence URI
    evidence_uri = f"evidence://{pkg_hash[:16]}"

    # 读取 session 信息
    import zipfile
    with zipfile.ZipFile(package_path, "r") as zf:
        session = json.loads(zf.read("session.json"))
        events_text = zf.read("events.jsonl").decode("utf-8")
        event_count = len([l for l in events_text.strip().split("\n") if l.strip()])
        ev_count = 0
        if "evidence.json" in zf.namelist():
            ev_count = len(json.loads(zf.read("evidence.json")))

    # 构建条目
    entry = {
        "evidence_uri": evidence_uri,
        "package_hash": pkg_hash,
        "session_id": session.get("session_id", ""),
        "session_objective": session.get("objective", ""),
        "event_count": event_count,
        "evidence_count": ev_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verified": True
    }

    # 追加到注册表
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Registered: {evidence_uri}")
    print(f"  Package: {Path(package_path).name}")
    print(f"  Events:  {event_count}")
    print(f"  Hash:    {pkg_hash[:16]}...")

def stats():
    if not REGISTRY_FILE.exists():
        print("No entries yet.")
        return

    entries = []
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    total_events = sum(e["event_count"] for e in entries)
    total_evidence = sum(e["evidence_count"] for e in entries)

    print(f"Registry Stats:")
    print(f"  Total Packages: {len(entries)}")
    print(f"  Total Events:   {total_events}")
    print(f"  Total Evidence: {total_evidence}")
    print(f"  All Verified:   {all(e['verified'] for e in entries)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python register.py <command>")
        print("  register <path>  注册一个 Evidence Package")
        print("  stats            查看注册表统计")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "register" and len(sys.argv) >= 3:
        register(sys.argv[2])
    elif cmd == "stats":
        stats()
    else:
        print("Unknown command")
