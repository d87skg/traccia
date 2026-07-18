# Traccia — Give your AI Agent a flight recorder.

Record every action. Replay every decision. Prove every execution. **In 5 minutes.**

## Install
```bash
pip install traccia-sdk
Quick Start
python
from traccia import observe

@observe
def my_agent():
    return "hello"

my_agent()
bash
traccia verify traccia-*.evidence
# → Valid OpenBase Evidence ✓
Commands
Command    What it does
traccia intercept    Record any agent's execution
traccia verify    Check evidence integrity
traccia diagnose    Find root cause of failures
traccia certify    Get OpenBase Certified badge
traccia guard    Block dangerous actions
Framework Support
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

OpenBase Protocol
Traccia is the official SDK for OpenBase — the open trust protocol for AI agents.

text
OpenBase = Protocol (what gets recorded)
Traccia  = SDK      (how you record it)
Links
OpenBase: https://github.com/d87skg/OpenBase

PyPI: https://pypi.org/project/traccia-sdk/

Paper: https://github.com/d87skg/traccia/releases/tag/v1.0.0

License
Apache 2.0
