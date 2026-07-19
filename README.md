# Traccia — the crash dump for AI agents

Debug, replay, and reproduce any agent failure. Like HAR files for the browser, but for autonomous agents.

## Install
```bash
pip install traccia-sdk
Quick Start
bash
traccia intercept -- python your_agent.py
traccia export failure.evidence
traccia replay failure.evidence
traccia diagnose failure.evidence
Commands
CommandWhat it does
traccia interceptCapture agent execution
traccia exportExport crash dump (.evidence bundle)
traccia replayReproduce the failure
traccia diagnoseFind root cause
traccia verifyCheck evidence integrity
traccia certifyGet OpenBase Certified badge
Framework Support
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

Links
GitHub: https://github.com/d87skg/traccia

PyPI: https://pypi.org/project/traccia-sdk/

Paper: https://github.com/d87skg/traccia/releases/tag/v1.0.0

License
Apache 2.0
