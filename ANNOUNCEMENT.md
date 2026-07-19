# We built a flight recorder for AI Agents

## The problem
AI agents fail silently. A tool call times out, a retry is missing, and you have no idea what happened. Logs tell you what the agent did, but not **why** it did it.

## What Traccia does
Traccia gives any AI agent a flight recorder. It records every decision, replays every execution, and diagnoses failures — in 5 minutes.

```bash
pip install traccia-sdk
traccia intercept -- python your_agent.py
traccia verify traccia-*.evidence
traccia diagnose traccia-*.evidence
How it works
Intercept: wraps any Python agent, captures every tool call and LLM request

Evidence: produces a verifiable .evidence package with hash-chain integrity

Replay: reconstructs the full execution timeline

Diagnose: finds root causes of failures

Framework support
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

Open source
Apache 2.0. GitHub: https://github.com/d87skg/traccia
PyPI: https://pypi.org/project/traccia-sdk/

What's next
We're collecting real-world agent failures to improve diagnosis accuracy. If your agent breaks in an interesting way, we want to see it.
