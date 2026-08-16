# Traccia

> **Debug AI Agent crashes in 5 minutes, not 5 hours.**

```bash
pip install traccia-sdk
traccia intercept -- python your_agent.py
When it crashes, replay the exact execution:
bash
traccia replay crash_*.evidence
📄 Paper · 📦 PyPI · 🤗 Dataset · 📖 OpenBase Protocol
The Problem
Your AI agent is running in production. It stops responding. No error log. No stack trace. Just silence.
You add print() statements. Restart. It works. You remove them. It breaks again.
You have no idea what actually happened.
The Solution
Traccia is a black box recorder for AI agents. Zero code changes.
Captures every tool call with full input/output
Records every LLM request/response
Pinpoints the exact failure with context
Generates tamper-proof .evidence files (SHA-256 chain)
30-Second Quick Start
bash
# 1. Install
pip install traccia-sdk

# 2. Intercept (no code changes!)
traccia intercept -- python my_agent.py

# 3. Replay after crash
traccia replay crash_*.evidence
What You Get
Python
# Example: A LangChain agent that silently loops
# Traccia evidence shows:
#   [14:30:22] ToolCall: search_tool(query="weather")
#   [14:30:23] ToolCall: search_tool(query="weather")  # same input!
#   [14:30:24] ToolCall: search_tool(query="weather")  # 23rd time...
#   [14:32:01] SILENT FAILURE: process alive, no output
Supported Frameworks
表格
Framework	Status	Notes
LangChain	✅ Full	traccia intercept -- python app.py
CrewAI	✅ Full	Zero config
AutoGen	✅ Full	Group chat supported
OpenAI Agents SDK	✅ Full	Tool calls + responses
Claude Code	✅ Beta	CLI interception
OpenHands	✅ Beta	Dev environment tracing
LangGraph	✅ Full	State transitions logged
Real-World Case Study
"Our customer service agent stopped responding at 2 AM. No logs. We added prints, restarted, and it worked—for 3 hours, then died again.
With Traccia, we replayed the .evidence file and saw the agent was calling search_tool 47 times with the exact same query. The LLM's observation format was wrong, so it thought the task was never complete.
Fixed in one line. Would have taken 6 hours of guessing without Traccia."
Installation
bash
pip install traccia-sdk
Requires Python 3.9+.
Usage
Basic Interception
bash
traccia intercept -- python my_agent.py
Replay a Crash
bash
traccia replay evidence_20250816_143022.evidence
Programmatic Access
Python
from traccia import observe

@observe  # 5 lines to full observability
def my_agent_run():
    ...
Evidence Format
Traccia produces .evidence files compatible with the OpenBase Protocol:
SHA-256 hash chain: Tamper-proof audit trail
23 standard event types (OBS v2.0): Tool calls, LLM requests, errors, state changes
Compression: 1000+ events compressed to 0.1% volume
4 fidelity levels: From summary to full replay
Benchmark Dataset
Traccia Benchmark on HuggingFace
100+ real-world execution traces from production AI agents:
Silent failures
Infinite loops
Tool errors (API timeout, wrong parameters)
LLM hallucinations (wrong tool selection)
Python
from datasets import load_dataset
ds = load_dataset("vasdvae/traccia-benchmark")
Architecture
plain
┌─────────────────────────────────────────┐
│  Your Agent (LangChain/CrewAI/AutoGen)  │
│  No code changes needed                   │
├─────────────────────────────────────────┤
│  Traccia Interceptor                    │
│  - Hooks into Python runtime             │
│  - Captures tool calls & LLM I/O         │
├─────────────────────────────────────────┤
│  OpenBase Protocol (OBS v2.0)             │
│  - Standardized event schema             │
│  - SHA-256 hash chain                    │
├─────────────────────────────────────────┤
│  .evidence File                         │
│  - Compressed, replayable, auditable     │
└─────────────────────────────────────────┘
Why Traccia vs Others?
表格
Traccia	LangSmith	AgentOps
Code changes	None (intercept --)	Add @traceable	Add @track
Crash replay	Full execution trace	Partial trace	Session only
Open source	✅ Apache 2.0	Partial	Partial
Self-hosted	✅ Fully	❌ Cloud only	❌ Cloud only
Price	Free	Per-trace billing	Per-event billing
Roadmap
[x] Core interception engine
[x] OpenBase Protocol v2.0
[x] 7 framework adapters
[x] Evidence compression (V1 engine)
[ ] Enterprise: SIEM integration, compliance reports, real-time alerts
[ ] TEE Extension: Hardware-level tamper resistance (interface frozen)
[ ] Network: Distributed evidence verification
Contributing
bash
git clone https://github.com/d87skg/traccia.git
cd traccia
pip install -e ".[dev]"
pytest  # 150+ tests
Citation
bibtex
@software{traccia2025,
  title={Traccia: Execution Evidence Layer for AI Agents},
  author={OpenBase Contributors},
  year={2025},
  url={https://github.com/d87skg/traccia}
}
⚠️ Not affiliated with traccia.ai. Traccia is an open-source execution evidence layer built on the OpenBase Protocol.
License
Apache 2.0. No API keys. No dashboard. No telemetry.
Traccia is part of the OpenBase ecosystem.
OpenBase Protocol · Traccia SDK · Benchmark Dataset
