# TRACCIA PROTOCOL v1.0

## 宪法声明

Session defines the objective.
Events define what happened.
Evidence proves it happened.
Attribution defines who is responsible.
Package preserves the truth.

## 协议层次

Level 0（必须实现）
- Session
- Event
- Evidence
- Package

Level 1（推荐实现）
- Replay

Level 2（可选实现）
- Attribution（需AES配合）

## 核心对象定义

### Session
一个完整目标的执行上下文。

字段：
- session_id: 全局唯一标识（UUID）
- objective: 目标描述（字符串）
- started_at: 开始时间（ISO 8601）
- ended_at: 结束时间（ISO 8601，可选）
- status: running | completed | failed | cancelled

### Event
一个不可再分的、可验证的原子行为事实。

三原则：
1. Atomic - 不可再拆
2. Immutable - 一旦生成，永远存在
3. Time Ordered - 必须存在时间顺序

字段：
- event_id: 全局唯一标识（UUID）
- session_id: 所属Session（UUID）
- timestamp: 发生时间（ISO 8601）
- event_type: 事件类型标签（字符串）
- actor_id: 执行主体标识（字符串）
- payload: 事件载荷（JSON对象）
- prev_hash: 前一个Event的SHA-256哈希（创世Event为null）
- hash: 本Event的SHA-256哈希

### Evidence
证明Event真实发生的材料。

核心原则：No Evidence = No Trust

字段：
- evidence_id: 全局唯一标识（UUID）
- event_id: 关联的Event（UUID）
- type: 证据类型（file_hash | screenshot | api_response | log_snapshot | binary_blob）
- sha256: 证据内容的SHA-256摘要
- storage_uri: 证据存储位置（URI）
- created_at: 证据生成时间（ISO 8601）

### Attribution
将行为与责任主体绑定。

字段：
- attribution_id: 全局唯一标识（UUID）
- session_id: 关联的Session（UUID）
- executor: 执行者标识（字符串，必填）
- supervisor: 监督者标识（字符串，可选）
- approver: 批准者标识（字符串，可选）
- policy_id: 适用策略ID（字符串，可选，预留给AES）

### Package
一个可独立验证的完整执行证明文件。

Package = Manifest + Session + Events + Evidence + Attribution + Signature

导出格式：task.evidence（ZIP压缩包）

内部结构：
- manifest.json
- session.json
- events.jsonl
- evidence/（目录）
- attribution.json（可选）
- signature.sig

## HashChain算法
hash_n = SHA-256( prev_hash + event_content_json )

text

创世Event：prev_hash = null

## 版本策略

- v1.0：五个核心对象冻结
- 后续版本：只能新增字段，不可删除或修改已有字段语义


## 协议约束规则（v1.0 冻结）

### Rule 1: Event 可关联多个 Evidence
一个 Event 允许拥有零个或多个 Evidence。
但每个 Evidence 必须关联一个且仅一个 Event。

### Rule 2: Evidence 不可脱离 Event
Evidence 是对 Event 的证明，不存在独立于 Event 的 Evidence。
删除 Event 时必须同步删除其所有关联 Evidence。

### Rule 3: Session 可包含多个 Agent
一个 Session 的 Events 可以来自不同的 actor_id。
责任划分由 Attribution 层负责。

### Rule 4: Package 不强制包含 Attribution
Attribution 是 Level 2（可选）。
没有 AES 的环境下，Traccia 必须能独立运行。
Package 缺少 Attribution 仍然有效。

### Rule 5: Event Type 开放
event_type 采用反向域名约定，但不强制注册。
内置类型：read_file, api_call, generate_response, execute_shell, click_button
自定义类型示例：custom.my_company.approval_flow
实现层应支持类型过滤，但不拒绝未知类型。

## v1.1 增量（2026-06-14）

### 新增 Evidence 类型：reference
为支持外部存储（如对象存储、文件系统），新增 `evidence_type` 枚举值 `"reference"`。

**Reference Evidence Schema：**
```json
{
  "evidence_type": "reference",
  "sha256": "证据内容的SHA-256摘要",
  "storage_uri": "s3://bucket/path/evidence.bin"
}

设计原则：

证据内容不内嵌于 Package，仅保存哈希和引用。

验证时需确认 URI 可访问且哈希匹配。

保持向后兼容：原有 file_hash 等类型不受影响。

