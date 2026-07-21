
Agent Execution Receipt (AER) Format v1.0
Status: FROZEN (90 days)
Also known as
.evidence Bundle = Agent Execution Receipt

Structure
text
task.evidence
├── manifest.json        # Package metadata
├── session.json         # Agent session record
├── events.jsonl         # Time-ordered canonical events
├── evidence.json        # Evidence records (optional)
├── attribution.json     # Attribution chain (optional)
└── signature.sig        # SHA-256 hash chain signature
Why "Agent Execution Receipt"?
Think of it as:

Crash dump for debugging

Flight recorder for replay

Audit receipt for compliance

Freeze Period
2026-07-19 to 2026-10-19
