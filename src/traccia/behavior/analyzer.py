import zipfile, json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any

class BehaviorAnalyzer:
    """Cross-Runtime Behavior Mining: 提取行为标签而非统一语义。"""

    def __init__(self, evidence_path: str):
        self.path = Path(evidence_path)
        self.events = self._load_events()

    def _load_events(self) -> List[Dict]:
        if not self.path.exists():
            return []
        with zipfile.ZipFile(self.path, 'r') as zf:
            if 'events.jsonl' in zf.namelist():
                lines = zf.read('events.jsonl').decode('utf-8').strip().split('\n')
                return [json.loads(line) for line in lines if line.strip()]
        return []

    # --- 1. Failure Shape ---
    def failure_shape(self) -> List[str]:
        """分析事件中的失败模式。"""
        failures = []
        for ev in self.events:
            payload = ev.get('payload', {})
            error_type = payload.get('type', '')
            error_msg = payload.get('error', '')
            # 关键词匹配（不依赖统一语义，基于原始字段）
            combined = f"{error_type} {error_msg}".lower()
            if 'timeout' in combined or 'timed out' in combined:
                failures.append('timeout')
            elif 'permission' in combined or 'denied' in combined:
                failures.append('permission_denied')
            elif 'not found' in combined or 'no such file' in combined or 'invalid' in combined:
                failures.append('invalid_action')
            elif 'loop' in combined or 'recursion' in combined:
                failures.append('loop_detected')
            elif ev.get('event_type') == 'error':
                failures.append('generic_error')
        return failures

    # --- 2. Recovery Behavior ---
    def recovery_behavior(self) -> List[str]:
        """推断恢复策略。"""
        recoveries = []
        # 简单启发：检查是否有重试、重新规划等模式
        event_types = [ev.get('event_type') for ev in self.events]
        if 'retry' in str(event_types).lower() or 'retry' in str(self.events).lower():
            recoveries.append('retry')
        if 'replan' in str(event_types).lower() or 'plan' in str(event_types).lower():
            recoveries.append('replan')
        if 'rollback' in str(event_types).lower():
            recoveries.append('rollback')
        if 'terminate' in str(event_types).lower() or 'exit' in str(event_types).lower():
            recoveries.append('terminate')
        if not recoveries:
            recoveries.append('unknown')
        return recoveries

    # --- 3. Temporal Structure ---
    def temporal_structure(self) -> str:
        """根据事件序列推断时间结构。"""
        event_types = [ev.get('event_type') for ev in self.events]
        unique_types = set(event_types)
        # 简单启发式
        if len(self.events) < 3:
            return 'single-step'
        if 'tool_call' in unique_types or 'shell_exec' in unique_types:
            # 检查是否有循环模式（相同事件多次出现）
            type_counts = Counter(event_types)
            if any(v > 5 for v in type_counts.values()):
                return 'loop'
            # 检查是否图结构（存在非顺序依赖，通过payload的_canonical_type或prev_hash判断）
            hashes = [ev.get('prev_hash') for ev in self.events if ev.get('prev_hash')]
            if len(hashes) > 1 and len(set(hashes)) < len(hashes):
                return 'dag'  # 可能不是简单链
            return 'interactive-session'
        return 'unknown'

    # --- 4. Execution Modality ---
    def execution_modality(self) -> str:
        """判断执行模态。"""
        event_types = [ev.get('event_type') for ev in self.events]
        unique_types = set(event_types)
        if 'shell_exec' in unique_types or 'file.read' in unique_types:
            return 'os-centric'
        if 'tool_call' in unique_types or 'llm_call' in unique_types:
            return 'tool-centric'
        if 'node_execute' in unique_types or 'graph_step' in unique_types:
            return 'graph-centric'
        if 'message' in unique_types or 'chat' in unique_types:
            return 'conversation-centric'
        return 'hybrid'

    # --- 综合报告 ---
    def report(self) -> Dict[str, Any]:
        return {
            "evidence": str(self.path.name),
            "event_count": len(self.events),
            "failure_shape": self.failure_shape(),
            "recovery_behavior": self.recovery_behavior(),
            "temporal_structure": self.temporal_structure(),
            "execution_modality": self.execution_modality(),
        }
