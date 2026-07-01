"""
TRACCIA PROTOCOL v1 - Package
"""

import json
import zipfile
import io
from typing import Any, Dict, List, Optional
from .session import Session
from .event import Event
from .evidence import Evidence
from .attribution import Attribution
from .utils import utc_now, sha256_hex, dict_to_json_stable


class Package:
    """
    Package：一个可独立验证的完整执行证明文件。

    Package = Manifest + Session + Events + Evidence + Attribution + Signature

    导出格式：task.evidence（ZIP压缩包）
    """

    def __init__(
        self,
        session: Session,
        events: List[Event],
        evidence_list: Optional[List[Evidence]] = None,
        attribution: Optional[Attribution] = None
    ):
        self.manifest = {
            "traccia_version": "1.0.0",
            "package_version": "1.0.0",
            "created_at": utc_now()
        }
        self.session = session
        self.events = events
        self.evidence_list = evidence_list or []
        self.attribution = attribution
        self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """生成 Package 的数字签名（当前为 SHA-256 简化实现）"""
        content = {
            "manifest": self.manifest,
            "session": self.session.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "evidence": [e.to_dict() for e in self.evidence_list]
        }
        if self.attribution:
            content["attribution"] = self.attribution.to_dict()

        content_json = dict_to_json_stable(content)
        return sha256_hex(content_json)

    def verify_signature(self) -> bool:
        """验证签名是否匹配"""
        return self._generate_signature() == self.signature

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "manifest": self.manifest,
            "session": self.session.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "evidence": [e.to_dict() for e in self.evidence_list],
            "signature": self.signature
        }
        if self.attribution:
            result["attribution"] = self.attribution.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        """序列化为完整 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def export_zip(self) -> bytes:
        """导出为 task.evidence ZIP 字节流"""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(self.manifest, indent=2))
            zf.writestr("session.json", json.dumps(self.session.to_dict(), indent=2))

            events_lines = "\n".join(
                json.dumps(e.to_dict(), ensure_ascii=False) for e in self.events
            )
            zf.writestr("events.jsonl", events_lines)

            if self.attribution:
                zf.writestr("attribution.json", json.dumps(self.attribution.to_dict(), indent=2))

            if self.evidence_list:
                zf.writestr("evidence.json", json.dumps(
                    [e.to_dict() for e in self.evidence_list], indent=2, ensure_ascii=False
                ))

            zf.writestr("signature.sig", self.signature)

        return buffer.getvalue()

    def save_zip(self, filepath: str) -> None:
        """保存 task.evidence 到磁盘"""
        with open(filepath, "wb") as f:
            f.write(self.export_zip())

    def __repr__(self):
        return f"Package({self.session.session_id[:8]}... | {len(self.events)} events | sig={self.signature[:12]}...)"