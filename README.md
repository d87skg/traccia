# Traccia

给你的 AI Agent 装个安全带。

---

## 安装

```bash
pip install traccia-guard
使用
python
from traccia_guard import GuardSession, BlockedActionError

session = GuardSession("部署新版本")

# 正常操作 — 通过
session.record("read_file", {"path": "/tmp/config.yaml"})

# 危险命令 — 被拦截
try:
    session.record("shell_exec", {"command": "rm -rf /"})
except BlockedActionError as e:
    print(f"已拦截: {e}")

# Token 异常 — 被警告
session.record("llm_call", {"token_count": 150000})
print(session.warnings)
规则
规则	检测	动作
dangerous_shell	rm -rf, sudo, chmod 777, mkfs, dd, fork bomb	BLOCK
token_spike	单次 > 100K tokens	WARN
internal_network	127.0.0.1, 192.168.x.x, 10.x.x.x, 172.16.x.x, localhost	BLOCK