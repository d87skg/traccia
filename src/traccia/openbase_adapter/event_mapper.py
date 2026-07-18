"""
Traccia → OBS Event Mapper
Converts free-text Traccia event labels to OBS 23 standard event types.
"""

TRACCIA_TO_OBS = {
    # Agent Lifecycle
    "agent_start": "AGENT_STARTED",
    "agent_finish": "AGENT_FINISHED",
    "agent_error": "AGENT_FAILED",
    "agent_pause": "AGENT_PAUSED",
    "agent_resume": "AGENT_RESUMED",
    "agent_created": "AGENT_CREATED",

    # Tool Execution
    "tool_start": "TOOL_CALL",
    "tool_finish": "TOOL_RESULT",
    "tool_error": "TOOL_ERROR",
    "api_call": "TOOL_CALL",
    "function_call": "TOOL_CALL",

    # LLM Interactions
    "llm_request": "LLM_REQUEST",
    "llm_response": "LLM_RESPONSE",
    "llm_stream_start": "LLM_STREAM_START",
    "llm_stream_end": "LLM_STREAM_END",
    "generate_response": "LLM_RESPONSE",

    # File Operations
    "read_file": "FILE_READ",
    "write_file": "FILE_WRITE",
    "file_read": "FILE_READ",
    "file_write": "FILE_WRITE",

    # Execution
    "execute_shell": "COMMAND_EXECUTE",
    "run_command": "COMMAND_EXECUTE",
    "execute_code": "CODE_EXECUTE",

    # Memory
    "memory_read": "MEMORY_READ",
    "memory_write": "MEMORY_WRITE",
    "memory_delete": "MEMORY_DELETE",

    # Human Interaction
    "approval_request": "APPROVAL_REQUEST",
    "approval_granted": "APPROVAL_GRANTED",
    "approval_denied": "APPROVAL_DENIED",
    "click_button": "TOOL_CALL",
}

OBS_TO_TRACCIA = {v: k for k, v in TRACCIA_TO_OBS.items()}

OBS_EVENT_TYPES = sorted(set(TRACCIA_TO_OBS.values()))

def to_obs(traccia_event_type: str) -> str:
    """Convert a Traccia event label to OBS event type."""
    if traccia_event_type in TRACCIA_TO_OBS:
        return TRACCIA_TO_OBS[traccia_event_type]
    if traccia_event_type.startswith("custom."):
        return traccia_event_type
    return traccia_event_type.upper()

def is_valid_obs(event_type: str) -> bool:
    """Check if an event type is a valid OBS type."""
    return event_type in OBS_EVENT_TYPES or event_type.startswith("custom.")
