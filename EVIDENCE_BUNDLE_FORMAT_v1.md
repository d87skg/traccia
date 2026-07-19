# .evidence Bundle Format v1.0

## Status: FROZEN (90 days)

## Structure
task.evidence
├── manifest.json # Package metadata
├── session.json # Agent session record
├── events.jsonl # Time-ordered canonical events
├── evidence.json # Evidence records (optional)
├── attribution.json # Attribution chain (optional)
└── signature.sig # SHA-256 hash chain signature

text

## Mandatory Fields
- manifest.json: traccia_version, package_version, created_at
- session.json: session_id, objective, started_at, status
- events.jsonl: event_id, session_id, timestamp, event_type, actor_id, payload, prev_hash, hash
- signature.sig: SHA-256 signature of all content

## Freeze Period
2026-07-19 to 2026-10-19

No new fields, no breaking changes.
