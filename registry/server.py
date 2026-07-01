import sys, json, hashlib, os, uuid, base64
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia.reference.python.validator import verify

REGISTRY_DIR = Path("D:/Traccia/registry")
CORPUS_DIR = REGISTRY_DIR / "corpus"
CORPUS_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = REGISTRY_DIR / "entries.jsonl"
UPLOAD_DIR = Path("D:/Traccia/evidence")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def load_entries():
    if not REGISTRY_FILE.exists():
        return []
    entries = []
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def register_package(path):
    if not Path(path).exists():
        return None, "file not found"
    result = verify(path)
    if not result.is_valid:
        return None, "verify failed"
    with open(path, "rb") as f:
        pkg_hash = hashlib.sha256(f.read()).hexdigest()
    import zipfile
    with zipfile.ZipFile(path, "r") as zf:
        session = json.loads(zf.read("session.json"))
        events_text = zf.read("events.jsonl").decode("utf-8")
        event_count = len([l for l in events_text.strip().split("\n") if l.strip()])
        ev_count = 0
        if "evidence.json" in zf.namelist():
            ev_count = len(json.loads(zf.read("evidence.json")))
    uri = f"evidence://{pkg_hash[:16]}"
    entry = {
        "evidence_uri": uri,
        "package_hash": pkg_hash,
        "session_id": session.get("session_id", ""),
        "session_objective": session.get("objective", ""),
        "event_count": event_count,
        "evidence_count": ev_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verified": True
    }
    with open(REGISTRY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry, None

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_GET(self):
        if self.path == "/api/stats":
            entries = load_entries()
            self._send_json({
                "total_packages": len(entries),
                "total_events": sum(e["event_count"] for e in entries),
                "total_evidence": sum(e["evidence_count"] for e in entries),
                "all_verified": all(e["verified"] for e in entries)
            })
        elif self.path == "/api/packages":
            self._send_json(load_entries())
        elif self.path.startswith("/api/verify/"):
            uri = self.path.replace("/api/verify/", "")
            entries = load_entries()
            match = [e for e in entries if e["evidence_uri"] == uri]
            self._send_json({"found": len(match) > 0, "entry": match[0] if match else None})
        elif self.path == "/":
            self._send_json({
                "service": "Traccia Evidence Corpus",
                "version": "0.2.0",
                "endpoints": ["/api/stats", "/api/packages", "/api/verify/:uri", "/api/register", "/api/upload"]
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/register":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            path = data.get("path", "")
            entry, error = register_package(path)
            if error:
                self._send_json({"error": error}, 400)
            else:
                self._send_json({"registered": entry["evidence_uri"], "entry": entry}, 201)
        elif self.path == "/api/upload":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            # 保存上传文件
            file_id = str(uuid.uuid4())
            file_path = CORPUS_DIR / f"{file_id}.evidence"
            with open(file_path, "wb") as f:
                f.write(raw_data)
            # 验证并注册
            entry, error = register_package(str(file_path))
            if error:
                # 移除无效文件
                file_path.unlink(missing_ok=True)
                self._send_json({"error": error}, 400)
            else:
                self._send_json({"uploaded": True, "evidence_uri": entry["evidence_uri"], "session_id": entry["session_id"]}, 201)
        else:
            self._send_json({"error": "not found"}, 404)

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == "__main__":
    port = 8765
    server = HTTPServer(("0.0.0.0", port), APIHandler)
    print(f"Traccia Corpus API running at http://localhost:{port}")
    print("Endpoints:")
    print("  GET  /api/stats")
    print("  GET  /api/packages")
    print("  GET  /api/verify/evidence://...")
    print("  POST /api/register  {path: 'task.evidence'}")
    print("  POST /api/upload    [binary evidence file]")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
