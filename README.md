# Traccia — OpenBase Developer SDK

Add verifiable execution to your AI agent in 5 lines.

## Install

`ash
pip install traccia-sdk
Quick Start
python
from traccia import observe

@observe
def my_agent():
    return agent.run()
bash
traccia intercept -- python your_agent.py
traccia diagnose traccia-*.evidence
Three Core Commands
CommandPurpose
traccia interceptAuto-generate OpenBase Evidence from any Python agent
traccia diagnoseAnalyze Evidence and output root cause report
traccia guardSecurity policy gateway between agent and tools
Framework Emitters
LangChain · CrewAI · AutoGen · OpenAI SDK · Claude Code · OpenHands · LangGraph

Relationship to OpenBase
text
OpenBase = Protocol (what gets recorded)
Traccia  = SDK      (how you record it)
OpenClaw = Reference Runtime
Links
OpenBase Protocol: https://github.com/d87skg/OpenBase

PyPI: https://pypi.org/project/traccia-sdk/

Paper: https://github.com/d87skg/traccia/releases/tag/v1.0.0

Dataset: https://huggingface.co/datasets/vasdvae/traccia-benchmark

License
Apache 2.0
