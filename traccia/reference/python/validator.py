"""
TRACCIA PROTOCOL v1 - Package Validator

用法：
    python -m traccia.reference.python.validator task.evidence
"""

import json
import zipfile
import sys
from typing import Tuple, List


class ValidationError:
    """验证错误"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.code}] {self.message}"


class ValidationResult:
    """验证结果"""
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []

    def add_error(self, code: str, message: str):
        self.errors.append(ValidationError(code, message))

    def add_warning(self, message: str):
        self.warnings.append(message)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def status(self) -> str:
        return "VALID" if self.is_valid else "TAMPERED"

    def report(self) -> str:
        lines = []
        lines.append(f"Status: {self.status}")
        lines.append(f"Errors: {len(self.errors)}")
        for e in self.errors:
            lines.append(f"  {e}")
        lines.append(f"Warnings: {len(self.warnings)}")
        for w in self.warnings:
            lines.append(f"  {w}")
        return "\n".join(lines)


class PackageValidator:
    """
    Package 验证器。

    验证流程：
    1. 结构验证 — ZIP 内部文件完整性
    2. Session 验证 — 必填字段检查
    3. Event Chain 验证 — HashChain 完整性
    4. Evidence 验证 — 关联完整性和 Hash 校验
    5. Signature 验证 — 签名一致性
    """

    def validate(self, filepath: str) -> ValidationResult:
        result = ValidationResult()

        try:
            with zipfile.ZipFile(filepath, "r") as zf:
                # Step 1: 结构验证
                self._validate_structure(zf, result)
                if not result.is_valid:
                    return result

                # 加载内容
                manifest = json.loads(zf.read("manifest.json"))
                session = json.loads(zf.read("session.json"))
                events = self._load_jsonl(zf.read("events.jsonl").decode("utf-8"))

                attribution = None
                if "attribution.json" in zf.namelist():
                    attribution = json.loads(zf.read("attribution.json"))

                evidence_list = []
                if "evidence.json" in zf.namelist():
                    evidence_list = json.loads(zf.read("evidence.json"))

                signature = zf.read("signature.sig").decode("utf-8").strip()

                # Step 2: Session 验证
                self._validate_session(session, result)

                # Step 3: Event Chain 验证
                self._validate_event_chain(events, result)

                # Step 4: Evidence 验证
                self._validate_evidence(evidence_list, events, result)

                # Step 5: Signature 验证
                self._validate_signature(
                    manifest, session, events, evidence_list, attribution, signature, result
                )

        except zipfile.BadZipFile:
            result.add_error("PKG-001", "不是有效的 ZIP 文件")
        except FileNotFoundError:
            result.add_error("PKG-002", f"文件不存在: {filepath}")
        except json.JSONDecodeError as e:
            result.add_error("PKG-003", f"JSON 解析错误: {e}")
        except Exception as e:
            result.add_error("PKG-999", f"未知错误: {e}")

        return result

    def _validate_structure(self, zf: zipfile.ZipFile, result: ValidationResult):
        """验证 ZIP 内部结构"""
        required = {"manifest.json", "session.json", "events.jsonl", "signature.sig"}
        actual = set(zf.namelist())

        missing = required - actual
        for f in missing:
            result.add_error("ST-001", f"缺少必要文件: {f}")

        if "events.jsonl" in actual:
            content = zf.read("events.jsonl").decode("utf-8").strip()
            if not content:
                result.add_error("ST-002", "events.jsonl 为空")

    def _validate_session(self, session: dict, result: ValidationResult):
        """验证 Session"""
        required = ["session_id", "objective", "started_at", "status"]
        for field in required:
            if field not in session or session[field] is None:
                result.add_error("SS-001", f"Session 缺少字段: {field}")

        valid_statuses = {"running", "completed", "failed", "cancelled"}
        if session.get("status") not in valid_statuses:
            result.add_error("SS-002", f"无效的 status: {session.get('status')}")

    def _validate_event_chain(self, events: list, result: ValidationResult):
        """验证 Event HashChain"""
        if not events:
            result.add_error("EV-001", "Event 列表为空")
            return

        for i, event in enumerate(events):
            # 检查必填字段
            for field in ["event_id", "session_id", "timestamp", "event_type", "actor_id", "hash"]:
                if field not in event or event[field] is None:
                    result.add_error("EV-002", f"Event[{i}] 缺少字段: {field}")

            # 验证 prev_hash
            if i == 0:
                # 创世Event: prev_hash 应为 None/null
                if event.get("prev_hash") is not None:
                    result.add_error(
                        "EV-003",
                        f"Event[{i}] 创世Event的prev_hash必须为null，实际为: {event.get('prev_hash')}"
                    )
            else:
                # 普通Event: prev_hash 应等于前一个Event的hash
                expected = events[i - 1].get("hash", "")
                actual = event.get("prev_hash", "")
                if actual != expected:
                    result.add_error(
                        "EV-004",
                        f"Event[{i}] HashChain断裂: "
                        f"期望prev_hash={expected[:16]}...，实际={actual[:16] if actual else 'None'}..."
                    )

    def _validate_evidence(self, evidence_list: list, events: list, result: ValidationResult):
        """验证 Evidence"""
        if not evidence_list:
            return

        event_ids = {e.get("event_id") for e in events}

        for i, ev in enumerate(evidence_list):
            # 检查必填字段
            for field in ["evidence_id", "event_id", "type", "sha256"]:
                if field not in ev or ev[field] is None:
                    result.add_error("EVD-001", f"Evidence[{i}] 缺少字段: {field}")

            # 验证关联的Event存在
            event_id = ev.get("event_id")
            if event_id and event_id not in event_ids:
                result.add_error(
                    "EVD-002",
                    f"Evidence[{i}] 关联的Event不存在: {event_id}"
                )

            # 验证 evidence type
            valid_types = {"file_hash", "screenshot", "api_response", "log_snapshot", "binary_blob"}
            ev_type = ev.get("type")
            if ev_type and ev_type not in valid_types:
                result.add_warning(f"Evidence[{i}] 未知类型: {ev_type}")

    def _validate_signature(
        self,
        manifest: dict,
        session: dict,
        events: list,
        evidence_list: list,
        attribution: dict | None,
        signature: str,
        result: ValidationResult
    ):
        """
        验证签名。

        与 package.py 的 _generate_signature 完全一致：
        - 使用 stable JSON（sort_keys）
        - content = manifest + session + events + evidence + attribution
        - SHA-256
        """
        from .utils import sha256_hex, dict_to_json_stable

        content = {
            "manifest": manifest,
            "session": session,
            "events": events,
            "evidence": evidence_list
        }
        if attribution:
            content["attribution"] = attribution

        content_json = dict_to_json_stable(content)
        expected_sig = sha256_hex(content_json)

        if expected_sig != signature:
            result.add_error(
                "SIG-001",
                f"签名不匹配: "
                f"期望={expected_sig[:16]}...，实际={signature[:16]}..."
            )

    def _load_jsonl(self, text: str) -> list:
        """加载 JSONL 格式"""
        events = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if line:
                events.append(json.loads(line))
        return events


def verify(filepath: str) -> ValidationResult:
    """便捷验证函数"""
    validator = PackageValidator()
    return validator.validate(filepath)


# CLI 入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python -m traccia.reference.python.validator <task.evidence>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = verify(filepath)
    print(result.report())
    sys.exit(0 if result.is_valid else 1)