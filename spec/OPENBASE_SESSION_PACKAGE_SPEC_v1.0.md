# OpenBase Session & Evidence Package Specification v1.0

## Status
Stable — formally adopted from Traccia SDK into OpenBase upper-layer standard.

## Position in OpenBase Architecture
OpenBase Core (OBS, Evidence, Replay, Conformance)
        |
Traccia SDK
        |
   ┌────┴────┐
   │ Session  │  ← Agent lifecycle boundary
   │ Package  │  ← Bundled execution trace (ZIP)
   └─────────┘

## Session Specification
Session defines the boundary of a single agent task execution.

```json
{
  "session_id": "uuid",
  "objective": "string",
  "started_at": "ISO8601",
  "ended_at": "ISO8601",
  "status": "running | completed | failed | cancelled",
  "runtime": "string",
  "metadata": {}
}
Evidence Package Specification
An Evidence Package is a ZIP archive containing all artifacts from one Session:

text
task.evidence
├── manifest.json        # Package metadata
├── session.json         # Session record
├── events.jsonl         # Time-ordered canonical events
├── evidence.json        # Evidence records (optional)
├── attribution.json     # Attribution chain (optional)
└── signature.sig        # SHA-256 hash chain signature
Relationship to OpenBase Core
Session and Package are NOT part of OpenBase Core.
They are SDK-layer constructs that wrap OpenBase Evidence and Replay primitives.
Different SDKs (Python, Rust, TypeScript) may implement Session/Package differently while producing the same underlying Evidence format.
