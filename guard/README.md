# Traccia Guard — Security Policy Gateway for AI Agents

Traccia Guard sits between your agent and its tools, enforcing a security policy. Stop agents from deleting databases, accessing internal networks, or exceeding token budgets—before it happens.

## Install

```bash
pip install traccia-guard
```

## Quick Start

```bash
traccia guard --auto -- python my_agent.py
```

## Built-in Policies
- `default`: blocks dangerous shell commands, internal network access, and token spikes
- `strict`: blocks all external tool calls by default, explicit allowlist only
- `permissive`: warns but does not block (audit mode)

## License
Apache 2.0
