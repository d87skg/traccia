"""
Traccia Evidence → OpenBase Evidence v2.0 Converter
Converts Traccia 6-field evidence to OpenBase 13-field evidence.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

def convert(
    traccia_event: Dict[str, Any],
    execution_id: str,
    agent_id: str,
    previous_hash: Optional[str] = None,
    vector_clock: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Convert a Traccia event dict to OpenBase Evidence v2.0 format.

    Args:
        traccia_event: Traccia event with fields: event_id, session_id, timestamp, event_type, actor_id, payload
        execution_id: Execution context identifier
        agent_id: Agent identifier
        previous_hash: Previous evidence hash (None for genesis)
        vector_clock: Current vector clock state

    Returns:
        OpenBase Evidence v2.0 dict with 13 required fields
    """
    evidence_id = f"evid_{uuid.uuid4().hex[:12]}"
    event_type = traccia_event.get("event_type", "AGENT_STARTED")

    if vector_clock is None:
        vector_clock = {}
    actor = agent_id
    vector_clock[actor] = vector_clock.get(actor, 0) + 1

    return {
        "evidence_id": evidence_id,
        "spec_version": "2.0",
        "event_id": traccia_event.get("event_id", ""),
        "execution_id": execution_id,
        "agent_id": agent_id,
        "event_type": event_type,
        "timestamp": traccia_event.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "causal": {
            "parent_id": previous_hash,
            "vector_clock": vector_clock,
        },
        "payload": traccia_event.get("payload", {}),
        "hash": "",
        "signature": "",
        "public_key": "",
    }

def batch_convert(
    traccia_events: list,
    execution_id: str,
    agent_id: str,
) -> list:
    """Convert a batch of Traccia events to OpenBase Evidence chain."""
    chain = []
    previous_hash = None
    vector_clock = {}

    for event in traccia_events:
        evidence = convert(event, execution_id, agent_id, previous_hash, vector_clock)
        chain.append(evidence)
        vector_clock = evidence["causal"]["vector_clock"]

    return chain
