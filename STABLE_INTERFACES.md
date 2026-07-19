# Traccia Stable Interfaces v1

The following three commands are frozen and will not change for 90 days:

| Command | Frozen Behavior |
|---------|----------------|
| `traccia intercept -- <cmd>` | Wraps any Python process, auto-generates `.evidence` |
| `traccia verify <file.evidence>` | Checks ZIP structure + HashChain, outputs PASS/FAIL |
| `traccia diagnose <file.evidence>` | Analyzes events, outputs root cause report |

## Output Format Stability
- `traccia verify` output: `Valid OpenBase Evidence` block with Agent, Events, Integrity, Replay
- `traccia diagnose` output: Diagnosis Report block with File, Valid, Anomalies, Root causes

## Freeze Period
2026-07-19 to 2026-10-19 (90 days)

No new parameters, no breaking changes to existing output formats.
