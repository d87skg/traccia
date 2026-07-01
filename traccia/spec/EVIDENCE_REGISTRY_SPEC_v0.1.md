# TRACCIA EVIDENCE REGISTRY SPEC v0.1

## 目标
为每个 Evidence Package 提供可引用、可验证的永久标识符。

## Registry Entry Schema
{
  "evidence_uri": "evidence://<hash>",
  "package_hash": "<sha256 of .evidence file>",
  "session_id": "<uuid>",
  "session_objective": "<string>",
  "event_count": <int>,
  "evidence_count": <int>,
  "created_at": "<iso8601>",
  "verified": true
}

## API
POST /register    — 注册一个 Package
GET  /verify/:uri — 验证一个 Package
GET  /stats       — 统计信息

## 存储
本地 JSON 文件: D:\Traccia\registry\entries.jsonl
