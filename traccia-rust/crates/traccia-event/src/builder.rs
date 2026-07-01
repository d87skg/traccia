use crate::model::Event;
use traccia_core::ids::new_id;
use traccia_core::time::now;

use aegis_adapters::TracciaAdapter;
use std::sync::Mutex;

static ADAPTER: Mutex<Option<TracciaAdapter>> = Mutex::new(None);

pub fn init_aegis() {
    let mut adapter = ADAPTER.lock().unwrap();
    *adapter = Some(TracciaAdapter::new());
}

fn record_to_aegis(event_type: &str, event_id: &str, detail: &str) {
    if let Ok(mut adapter) = ADAPTER.lock() {
        if let Some(ref mut a) = *adapter {
            let _ = a.record_event(event_type, event_id, detail);
        }
    }
}

pub struct EventBuilder {
    session_id: String,
    event_type: String,
    actor_id: String,
    payload: serde_json::Value,
    prev_hash: String,
}

impl EventBuilder {
    pub fn new(session_id: &str, event_type: &str, actor_id: &str) -> Self {
        Self {
            session_id: session_id.to_string(),
            event_type: event_type.to_string(),
            actor_id: actor_id.to_string(),
            payload: serde_json::Value::Null,
            prev_hash: String::new(),
        }
    }

    pub fn payload(mut self, payload: serde_json::Value) -> Self {
        self.payload = payload;
        self
    }

    pub fn prev_hash(mut self, prev_hash: &str) -> Self {
        self.prev_hash = prev_hash.to_string();
        self
    }

    pub fn build(self) -> Event {
        let event_id = new_id();
        let timestamp = now();

        let mut event = Event {
            event_id: event_id.clone(),
            session_id: self.session_id,
            timestamp,
            event_type: self.event_type.clone(),
            actor_id: self.actor_id,
            payload: self.payload,
            prev_hash: self.prev_hash,
            hash: String::new(),
        };

        event.hash = event.compute_hash();

        // Aegis Proof 记录
        record_to_aegis(&self.event_type, &event_id, "Event created");

        event
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_builder_creates_event() {
        init_aegis();

        let event = EventBuilder::new("sess-1", "api_call", "agent_001")
            .payload(serde_json::json!({"url": "https://api.example.com"}))
            .build();

        assert_eq!(event.event_type, "api_call");
        assert!(!event.hash.is_empty());
    }

    #[test]
    fn test_builder_chain() {
        init_aegis();

        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .payload(serde_json::json!({"file": "/data/a.csv"}))
            .build();

        let e2 = EventBuilder::new("sess-1", "api_call", "agent_001")
            .prev_hash(&e1.hash)
            .build();

        assert!(e2.verify_chain_link(Some(&e1)));
    }
}