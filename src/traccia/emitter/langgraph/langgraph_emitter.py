import sys, functools
from pathlib import Path
from typing import Any, Dict, Optional

_src_path = Path("D:/Traccia/src/traccia")
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder import Recorder

class LangGraphEmitter:
    """Emitter for LangGraph. Hooks into StateGraph nodes and edges to record execution."""

    def __init__(self, recorder: Recorder):
        self._recorder = recorder

    def patch_graph(self, graph):
        """Patch a compiled LangGraph StateGraph to emit events on node execution."""
        if hasattr(graph, 'nodes'):
            for node_name, node_fn in graph.nodes.items():
                graph.nodes[node_name] = self._wrap_node(node_name, node_fn)
        return graph

    def _wrap_node(self, node_name: str, original_fn):
        @functools.wraps(original_fn)
        def wrapper(state, *args, **kwargs):
            try:
                self._recorder.observe_tool(
                    tool_name=f"graph.node.{node_name}",
                    input={"state": str(state)[:200]},
                    output={},
                    metadata={"node": node_name, "type": "langgraph_node_start"}
                )
                result = original_fn(state, *args, **kwargs)
                self._recorder.observe_tool(
                    tool_name=f"graph.node.{node_name}",
                    input={},
                    output={"state": str(result)[:200]},
                    metadata={"node": node_name, "type": "langgraph_node_end"}
                )
                return result
            except Exception as e:
                self._recorder.observe_error(e, {"node": node_name})
                raise
        return wrapper
