> ⚠️ **This is NOT the observability platform at [traccia.ai](https://traccia.ai).**  
> Traccia is the **compression and verification layer for autonomous agent execution.**  
> Built on the [OpenBase Protocol](https://github.com/d87skg/OpenBase).

---

# Traccia — Verifiable Execution Summary for AI Agents

Turn millions of agent events into a 5KB verifiable proof. Trust through verification, not promises.

## Install
```bash
pip install traccia-sdk
Quick Start
bash
traccia intercept -- python your_agent.py
traccia replay traccia-*.evidence
traccia diagnose traccia-*.evidence
Before & After
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

Why Traccia?
Crash dump for agents — Like a core dump, but for AI. Every failure becomes reproducible.

Flight recorder — Replay the exact execution timeline. See every decision.

Audit receipt — Hash-chain verified evidence. Prove what your agent did.

5 lines of code — No config, no dashboard, no API key. Just pip install.

Trust through verification, not promises — Your agent works for you. Traccia proves it.

Built on OpenBase
Traccia is the official SDK for OpenBase — the open trust protocol for AI agents.

text
Traccia  = SDK      (how you record it)
OpenBase = Protocol (what gets recorded)
Compressor Extension — Verifiable Execution Summary (100MB → 5KB)

Roadmap
Now: Black box recorder — capture, replay, diagnose

Next: OpenBase OTEL Bridge — enterprise observability integration

Future: Quantum-ready execution evidence (obs-quantum extension)

Open Source
Apache 2.0. No API keys. No dashboard. No telemetry.

https://github.com/d87skg/traccia

Feedback
Found a bug? Have a feature idea? Open an issue.

Just want to share your experience? Start a discussion.

License
Apache 2.0
