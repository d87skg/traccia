use aegis_adapters::TracciaAdapter;
use std::sync::Mutex;

static ADAPTER: Mutex<Option<TracciaAdapter>> = Mutex::new(None);

pub fn init_aegis() {
    let mut adapter = ADAPTER.lock().unwrap();
    *adapter = Some(TracciaAdapter::new());
}

pub fn record_to_aegis(event: &str, task_id: &str, detail: &str) -> serde_json::Value {
    let mut adapter = ADAPTER.lock().unwrap();
    match adapter.as_mut() {
        Some(a) => a.record_event(event, task_id, detail),
        None => serde_json::json!({"error": "Aegis not initialized"}),
    }
}

pub mod model;
pub mod builder;

pub use model::Event;
pub use builder::EventBuilder;
