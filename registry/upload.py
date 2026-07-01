import sys
import requests
from pathlib import Path

def upload(file_path, server_url="http://localhost:8765/api/upload"):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    with open(path, "rb") as f:
        response = requests.post(server_url, data=f.read())

    if response.status_code == 201:
        data = response.json()
        print(f"Uploaded successfully!")
        print(f"Evidence URI: {data.get('evidence_uri')}")
        print(f"Session ID: {data.get('session_id')}")
    else:
        print(f"Upload failed: {response.json().get('error', 'unknown error')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload.py <file.evidence>")
        sys.exit(1)
    upload(sys.argv[1])
