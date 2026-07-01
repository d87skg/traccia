use serde::{Deserialize, Serialize};
use traccia_core::ids::new_id;
use traccia_core::time::now;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimelineEntry {
    pub timestamp: String,
    pub event_id: String,
    pub event_type: String,
    pub title: String,
    pub actor_id: String,
    pub evidence_count: usize,
    pub summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Timeline {
    pub timeline_id: String,
    pub session_id: String,
    pub session_objective: String,
    pub generated_at: String,
    pub entries: Vec<TimelineEntry>,
}

impl Timeline {
    pub fn new(session_id: &str, session_objective: &str) -> Self {
        Self {
            timeline_id: new_id(),
            session_id: session_id.to_string(),
            session_objective: session_objective.to_string(),
            generated_at: now(),
            entries: Vec::new(),
        }
    }

    pub fn add_entry(&mut self, entry: TimelineEntry) {
        self.entries.push(entry);
    }
}
