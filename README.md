> ⚠️ **This is NOT the observability platform at [traccia.ai](https://traccia.ai).**
> Traccia is the **black box recorder for AI agents** — capture, replay, and debug any agent failure in 5 lines of code.
> Built on the [OpenBase Protocol](https://github.com/d87skg/OpenBase).

---

# Traccia — The Black Box Recorder for AI Agents

Capture, replay, and debug autonomous AI agents in 5 lines of code.

```bash
pip install traccia-sdk
bash
traccia intercept -- python your_agent.py
traccia verify traccia-*.evidence
traccia diagnose traccia-*.evidence
What It Does
Command	What It Does
traccia intercept	Record any agent's execution — every tool call, every LLM request
traccia verify	Check evidence integrity — hash-chain verified
traccia diagnose	Find root cause of failures — "Why did my agent crash?"
traccia certify	Get OpenBase Certified badge for your README
traccia guard	Block dangerous actions before they happen
Supported Frameworks
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

Why Traccia?
Crash dump for agents — Like a core dump, but for AI. Every failure becomes reproducible.

Flight recorder — Replay the exact execution timeline. See every decision.

Audit receipt — Hash-chain verified evidence. Prove what your agent did.

5 lines of code — No config, no dashboard, no API key. Just pip install.

Roadmap
Now: Black box recorder — capture, replay, diagnose

Next: OpenBase OTEL Bridge — enterprise observability integration

Future: Quantum-ready execution evidence

Built on OpenBase
Traccia is the official SDK for OpenBase — the open trust protocol for AI agents.

text
Traccia  = SDK      (how you record it)
OpenBase = Protocol (what gets recorded)
Links
GitHub: https://github.com/d87skg/traccia

PyPI: https://pypi.org/project/traccia-sdk/

Paper: https://github.com/d87skg/traccia/releases/tag/v1.0.0

License
Apache 2.0
