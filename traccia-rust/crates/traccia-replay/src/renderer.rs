use crate::timeline::Timeline;

pub struct TimelineRenderer;

impl TimelineRenderer {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, timeline: &Timeline, format: &str) -> String {
        match format {
            "json" => self.render_json(timeline),
            "md" | "markdown" => self.render_markdown(timeline),
            _ => self.render_text(timeline),
        }
    }

    fn render_text(&self, timeline: &Timeline) -> String {
        let mut lines = Vec::new();
        lines.push(format!("Session: {}", timeline.session_objective));
        lines.push("─".repeat(50));

        if timeline.entries.is_empty() {
            lines.push("(无事件)".to_string());
            return lines.join("\n");
        }

        for entry in &timeline.entries {
            let time_str = extract_time(&entry.timestamp);
            lines.push(format!("\n[{}] {}", time_str, entry.title));
            if !entry.summary.is_empty() {
                lines.push(format!("           {}", entry.summary));
            }
            if entry.evidence_count > 0 {
                lines.push(format!("           Evidence: {}", entry.evidence_count));
            }
        }

        lines.join("\n")
    }

    fn render_markdown(&self, timeline: &Timeline) -> String {
        let mut lines = Vec::new();
        lines.push(format!("# Session: {}", timeline.session_objective));
        lines.push(String::new());
        lines.push("## Timeline".to_string());
        lines.push(String::new());

        if timeline.entries.is_empty() {
            lines.push("*(无事件)*".to_string());
            return lines.join("\n");
        }

        for entry in &timeline.entries {
            let time_str = extract_time(&entry.timestamp);
            lines.push(format!("### {} — {}", time_str, entry.title));
            lines.push(String::new());
            lines.push(format!("- **Type**: {}", entry.event_type));
            lines.push(format!("- **Actor**: {}", entry.actor_id));
            if !entry.summary.is_empty() {
                lines.push(format!("- **Summary**: {}", entry.summary));
            }
            if entry.evidence_count > 0 {
                lines.push(format!("- **Evidence**: {}", entry.evidence_count));
            }
            lines.push(String::new());
        }

        lines.join("\n")
    }

    fn render_json(&self, timeline: &Timeline) -> String {
        serde_json::to_string_pretty(timeline).unwrap_or_default()
    }
}

impl Default for TimelineRenderer {
    fn default() -> Self {
        Self::new()
    }
}

fn extract_time(timestamp: &str) -> String {
    // 从 ISO 8601 提取 HH:MM:SS
    if let Some(t_pos) = timestamp.find('T') {
        let time_part = &timestamp[t_pos + 1..];
        let time_part = time_part.split('.').next().unwrap_or(time_part);
        let time_part = time_part.trim_end_matches('Z').trim_end_matches('+');
        time_part.to_string()
    } else {
        timestamp.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::timeline::{Timeline, TimelineEntry};

    #[test]
    fn test_render_text() {
        let mut timeline = Timeline::new("sess-1", "测试会话");
        timeline.add_entry(TimelineEntry {
            timestamp: "2026-06-08T10:01:12Z".to_string(),
            event_id: "evt-1".to_string(),
            event_type: "read_file".to_string(),
            title: "读取文件".to_string(),
            actor_id: "agent_001".to_string(),
            evidence_count: 2,
            summary: "读取了 /data/test.csv".to_string(),
        });

        let renderer = TimelineRenderer::new();
        let output = renderer.render(&timeline, "text");

        assert!(output.contains("测试会话"));
        assert!(output.contains("读取文件"));
        assert!(output.contains("Evidence: 2"));
    }

    #[test]
    fn test_render_json() {
        let timeline = Timeline::new("sess-1", "测试");
        let renderer = TimelineRenderer::new();
        let output = renderer.render(&timeline, "json");

        assert!(output.contains("timeline_id"));
        assert!(output.contains("sess-1"));
    }
}
