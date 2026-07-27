> ⚠️ **This is NOT the observability platform at traccia.ai.**  
> Traccia is a **flight recorder for AI agents** — find out why your agent failed, in 60 seconds.

---

# Agent crashed? Find out why in 60 seconds.

```bash
pip install traccia-sdk
traccia intercept -- python your_agent.py
traccia replay traccia-*.evidence
Before	After
"Agent failed, no idea why"	Replay the exact failure timeline
"Claude Code deleted the wrong file"	See every tool call that led to it
"Cursor called the wrong tool"	Trace the exact prompt and response
"AutoGen infinite loop"	Pinpoint the retry that caused it
Works With Your Stack
LangChain · LangGraph · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands

One Command, Full Trace
text
$ traccia intercept -- python agent.py
Agent failed at step 17: Tool 'delete_file' called with /src

$ traccia replay failure.evidence
┌──────────┬─────────────┬──────────┐
│ Step 12  │ llm.call    │ "I should clean up unused files"  │
│ Step 17  │ tool.call   │ delete_file("/src") ← ROOT CAUSE │
└──────────┴─────────────┴──────────┘
Real Cases
Claude Code deleted wrong files → Replay showed prompt contamination at step 12

Cursor called wrong tool → Trace revealed schema mismatch in tool definition

AutoGen infinite loop → Timeline exposed missing retry limit at step 5

Open Source
Apache 2.0. No API keys. No dashboard. No telemetry.

https://github.com/d87skg/traccia
