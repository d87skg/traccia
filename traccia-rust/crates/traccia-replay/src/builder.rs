use crate::timeline::{Timeline, TimelineEntry};
use std::collections::HashMap;

/// event_type → 人类可读标题
fn event_title(event_type: &str) -> String {
    match event_type {
        "read_file" => "读取文件".to_string(),
        "write_file" => "写入文件".to_string(),
        "api_call" => "API 调用".to_string(),
        "generate_response" => "生成回复".to_string(),
        "execute_shell" => "执行 Shell 命令".to_string(),
        "click_button" => "点击按钮".to_string(),
        _ => event_type.to_string(),
    }
}

/// 根据事件类型和 payload 构建摘要
fn event_summary(event_type: &str, payload: &serde_json::Value) -> String {
    match event_type {
        "read_file" => format!("读取了 {}", payload.get("file_path").and_then(|v| v.as_str()).unwrap_or("未知文件")),
        "api_call" => format!("调用了 {}", payload.get("endpoint").and_then(|v| v.as_str()).unwrap_or("未知接口")),
        "generate_response" => format!("生成了 {} 格式的 {}", 
            payload.get("format").and_then(|v| v.as_str()).unwrap_or(""),
            payload.get("output_type").and_then(|v| v.as_str()).unwrap_or("回复")
        ),
        "execute_shell" => format!("执行命令: {}", payload.get("command").and_then(|v| v.as_str()).unwrap_or("未知")),
        _ => String::new(),
    }
}

pub struct ReplayBuilder;

impl ReplayBuilder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(
        &self,
        session_id: &str,
        session_objective: &str,
        events: &[traccia_event::Event],
        evidences: &[traccia_evidence::Evidence],
    ) -> Timeline {
        // 构建 evidence 计数表: event_id → count
        let mut evidence_count: HashMap<&str, usize> = HashMap::new();
        for ev in evidences {
            *evidence_count.entry(&ev.event_id).or_insert(0) += 1;
        }

        let mut timeline = Timeline::new(session_id, session_objective);

        for event in events {
            let count = evidence_count.get(event.event_id.as_str()).copied().unwrap_or(0);
            let entry = TimelineEntry {
                timestamp: event.timestamp.clone(),
                event_id: event.event_id.clone(),
                event_type: event.event_type.clone(),
                title: event_title(&event.event_type),
                actor_id: event.actor_id.clone(),
                evidence_count: count,
                summary: event_summary(&event.event_type, &event.payload),
            };
            timeline.add_entry(entry);
        }

        timeline
    }
}

impl Default for ReplayBuilder {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use traccia_event::EventBuilder;
    use traccia_evidence::{Evidence, EvidenceType};

    #[test]
    fn test_build_timeline() {
        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .payload(serde_json::json!({"file_path": "/data/q3.csv"}))
            .build();

        let ev1 = Evidence::new(&e1.event_id, EvidenceType::FileHash, "hash123", "file:///evd.bin");

        let builder = ReplayBuilder::new();
        let timeline = builder.build("sess-1", "生成Q3报告", &[e1], &[ev1]);

        assert_eq!(timeline.session_objective, "生成Q3报告");
        assert_eq!(timeline.entries.len(), 1);
        assert_eq!(timeline.entries[0].title, "读取文件");
        assert_eq!(timeline.entries[0].evidence_count, 1);
    }
}
