# Traccia — the flight recorder for AI agents

Debug, replay, and verify any agent failure in minutes.

## Quick Start
```bash
pip install traccia-sdk
traccia intercept -- python your_agent.py
traccia verify traccia-*.evidence
traccia diagnose traccia-*.evidence
What it does
Intercept: wraps any Python agent, captures every tool call and LLM request

Evidence: produces a verifiable .evidence package with hash-chain integrity

Replay: reconstructs the full execution timeline

Diagnose: finds root causes of failures

Framework support
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

Open source
Apache 2.0. GitHub: https://github.com/d87skg/traccia
PyPI: https://pypi.org/project/traccia-sdk/
