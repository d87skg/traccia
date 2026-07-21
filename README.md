> ⚠️ **This is NOT the observability platform at [traccia.ai](https://traccia.ai).**  
> Traccia SDK is the **Execution Evidence Layer** for AI agents — making autonomous agent behavior provable, reproducible, and auditable.

---

# Traccia — Execution Evidence for AI Agents

Think of it as a **crash dump + flight recorder + audit receipt** for autonomous agents.

## Install
```bash
pip install traccia-sdk


Quick Start
bash
traccia intercept -- python your_agent.py
traccia verify traccia-*.evidence
traccia diagnose traccia-*.evidence

Commands
Command	What it does
traccia intercept	Record any agent's execution
traccia verify	Check evidence integrity
traccia diagnose	Find root cause of failures
traccia certify	Get OpenBase Certified badge
traccia guard	Block dangerous actions
Framework Support
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

OpenBase Protocol
Traccia is the official SDK for OpenBase — the open trust protocol for AI agents.

OpenBase = Protocol (what gets recorded)
Traccia  = SDK      (how you record it)

Links
GitHub: https://github.com/d87skg/traccia

PyPI: https://pypi.org/project/traccia-sdk/

Paper: https://github.com/d87skg/traccia/releases/tag/v1.0.0

License
Apache 2.0

