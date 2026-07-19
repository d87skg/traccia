"""
TRACCIA PROTOCOL v1 - 基础工具
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict


def generate_uuid() -> str:
    """生成 UUID v4 字符串"""
    return str(uuid.uuid4())


def utc_now() -> str:
    """返回 UTC 时间的 ISO 8601 格式字符串"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_hex(data: str) -> str:
    """计算字符串的 SHA-256 哈希，返回十六进制字符串"""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def dict_to_json_stable(d: Dict[str, Any]) -> str:
    """
    将字典转为稳定的 JSON 字符串。
    保证键排序一致，用于哈希计算。
    """
    return json.dumps(d, sort_keys=True, ensure_ascii=False)


def validate_required_fields(data: Dict[str, Any], required: list) -> None:
    """
    简易字段校验，缺少必填字段时抛出 ValueError。
    允许字段值为 None（如 prev_hash）。
    """
    for field in required:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")