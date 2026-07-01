# TRACCIA REPLAY SPEC v0.1

## 核心对象

### Timeline
Session 的可阅读视图。将机器事实转换为人类可理解的叙事。

字段：
- timeline_id: 全局唯一标识（UUID）
- session_id: 关联的 Session（UUID）
- session_objective: Session 目标描述
- generated_at: 生成时间（ISO 8601）
- entries: TimelineEntry 列表

### TimelineEntry
时间线上的单个节点。

字段：
- timestamp: 发生时间
- event_id: 关联的 Event
- event_type: 事件类型
- title: 人类可读的事件标题
- summary: 事件摘要（可选）
- actor_id: 执行主体
- evidence_count: 关联证据数量

## 架构

### builder.py
Package → Timeline 转换。

### renderer.py
Timeline → 多格式输出（Text / Markdown / JSON）。

### filters.py
Timeline 过滤器（event_type / time_range / actor）。

## 输出格式

### Text（默认）
Session: <objective>
─────────────────────────────
[HH:MM:SS] <title>
Evidence: N

### Markdown
```markdown
# Session: <objective>
## Timeline
### HH:MM:SS — <title>
- Type: <event_type>
- Evidence: N
SON
标准 Timeline JSON 结构。

约束
Timeline 是只读视图，不修改原始 Event

Narrative 是派生视图，LLM 可解释但不可修改事实

与 AES 组合可生成 Accountability Timeline



