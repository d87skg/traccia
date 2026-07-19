import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# 使用原始 Guard 规则
_guard_path = Path(__file__).parent.parent.parent.parent.parent / 'guard' / 'src' / 'traccia_guard'
if str(_guard_path) not in sys.path:
    sys.path.insert(0, str(_guard_path))

from rules import evaluate as guard_evaluate, BlockedActionError

from ..middleware import Middleware, Action

class GuardMiddleware(Middleware):
    def process(self, event: Dict[str, Any]) -> Tuple[Dict[str, Any], Action]:
        payload = event.get('payload', {})
        action, msg = guard_evaluate(payload)
        if action == 'BLOCK':
            raise BlockedActionError(msg)
        # WARN 暂不抛出异常，只记录（可扩展）
        return event, Action.PASS
