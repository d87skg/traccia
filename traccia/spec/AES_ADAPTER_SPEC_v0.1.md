# TRACCIA AES ADAPTER SPEC v0.1

## 设计原则

Traccia 独立于 AES 存在。
AES 是 AttributionProvider 的一种实现。
Traccia 定义接口，AES 负责解析责任。

## 核心接口

### AttributionProvider（抽象）

```python
class AttributionProvider(ABC):
    def resolve_session(self, session_id: str) -> ResponsibilityRecord
    def resolve_event(self, event_id: str) -> ResponsibilityRecord

    不出现 "AES" 字样。
任何责任解析系统都可实现此接口。

AESProvider（具体实现）
python
class AESProvider(AttributionProvider):
    def __init__(self, aes_endpoint: str)
新增核心对象
ResponsibilityRecord
字段：

record_id: UUID

subject_id: 关联的 session_id 或 event_id

subject_type: "session" | "event"

executor: Actor

supervisor: Actor（可选）

approver: Actor（可选）

policy_id: 策略 ID（可选）

risk_level: "low" | "medium" | "high" | "critical"

resolved_at: 解析时间

Actor
字段：

id: 主体标识

type: "agent" | "human" | "workflow" | "committee"

ResponsibilityChain
一个 Session 内多个责任分配记录的有序集合。

字段：

chain_id: UUID

session_id: UUID

links: ResponsibilityLink[]

ResponsibilityLink
字段：

actor: Actor

role: "executor" | "supervisor" | "approver"

timestamp: 指定时间

comment: 备注（可选）

Attribution v2 升级
从 v1 的扁平字段升级为结构化 Actor：

json
{
  "attribution_id": "uuid",
  "session_id": "uuid",
  "executor": {
    "id": "agent_001",
    "type": "agent"
  },
  "supervisor": {
    "id": "human_001",
    "type": "human"
  },
  "approver": {
    "id": "ceo_001",
    "type": "human"
  },
  "policy_id": "AES-RISK-001",
  "risk_level": "medium",
  "chain": []
}
Package v2 升级
attribution 从单个对象改为数组：

json
{
  "attribution": []
}
支持一个 Session 内多个责任链。

Replay + Attribution
Timeline Entry 增加 responsibility 字段：

json
{
  "timestamp": "...",
  "title": "读取文件",
  "responsibility": {
    "executor": "agent_001",
    "risk_level": "low"
  }
}
Replay 输出变为 Accountability Timeline：

text
[10:01:12] 读取文件
           Executor: agent_001
           Risk: low