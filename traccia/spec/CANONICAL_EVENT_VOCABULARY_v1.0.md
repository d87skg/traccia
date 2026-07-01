# Traccia Canonical Event Vocabulary v1.0

## Purpose
Define a universal set of event types for AI agent execution traces. Every framework-specific event must be mapped to one of these canonical types.

## Canonical Event Types

### Agent Lifecycle
- **session.start** : Agent begins a task.
- **session.end** : Agent completes a task.
- **session.fail** : Agent fails a task.

### LLM Interactions
- **llm.request** : LLM API call initiated.
- **llm.response** : LLM response received.
- **llm.error** : LLM call failed.

### Tool Interactions
- **tool.invoke** : Tool execution started.
- **tool.result** : Tool execution result.
- **tool.error** : Tool execution failed.

### File System
- **file.read** : File read operation.
- **file.write** : File write operation.
- **file.delete** : File deletion.

### Network
- **http.request** : Outgoing HTTP request.
- **http.response** : Incoming HTTP response.

### Memory / State
- **memory.read** : Agent reads from memory.
- **memory.write** : Agent writes to memory.

### Errors & Control
- **error.generic** : Generic runtime error.
- **retry.attempt** : Retry attempt.
- **agent.think** : Agent internal reasoning step (optional).

## Mapping Rules
- Each Emitter must translate native events into these canonical types.
- Additional metadata may be stored in the payload.
- The Recorder layer must accept both raw and canonical events.
