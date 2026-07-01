use serde::{Deserialize, Serialize};

/// Event：一个不可再分的、可验证的原子行为事实。
///
/// HashChain 算法：
///     hash = SHA-256( prev_hash + content_json )
///
/// 创世Event 的 prev_hash 为空字符串。
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Event {
    pub event_id: String,
    pub session_id: String,
    pub timestamp: String,
    pub event_type: String,
    pub actor_id: String,
    pub payload: serde_json::Value,
    pub prev_hash: String,
    pub hash: String,
}

impl Event {
    /// 计算本 Event 的 SHA-256 哈希
    pub fn compute_hash(&self) -> String {
        let content = serde_json::json!({
            "event_id": self.event_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        });
        let content_str = serde_json::to_string(&content).unwrap_or_default();
        let combined = format!("{}{}", self.prev_hash, content_str);
        traccia_core::hash::sha256(&combined)
    }

    /// 验证与前一事件的链上关系
    pub fn verify_chain_link(&self, prev_event: Option<&Event>) -> bool {
        match prev_event {
            None => self.prev_hash.is_empty(),
            Some(prev) => self.prev_hash == prev.hash,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_event(prev_hash: &str) -> Event {
        Event {
            event_id: traccia_core::ids::new_id(),
            session_id: traccia_core::ids::new_id(),
            timestamp: traccia_core::time::now(),
            event_type: "read_file".to_string(),
            actor_id: "agent_001".to_string(),
            payload: serde_json::json!({"file": "/data/q3.csv"}),
            prev_hash: prev_hash.to_string(),
            hash: String::new(),
        }
    }

    #[test]
    fn test_genesis_event_prev_hash_empty() {
        let event = make_event("");
        assert!(event.prev_hash.is_empty());
    }

    #[test]
    fn test_hash_is_deterministic() {
        let mut e1 = make_event("");
        e1.hash = e1.compute_hash();

        let mut e2 = make_event("");
        e2.hash = e2.compute_hash();

        // 相同内容但不同 event_id，hash 应该不同
        assert_ne!(e1.hash, e2.hash);
    }

    #[test]
    fn test_chain_link_genesis() {
        let event = make_event("");
        assert!(event.verify_chain_link(None));
    }

    #[test]
    fn test_chain_link_valid() {
        let mut e1 = make_event("");
        e1.hash = e1.compute_hash();

        let mut e2 = make_event(&e1.hash);
        e2.hash = e2.compute_hash();

        assert!(e2.verify_chain_link(Some(&e1)));
    }

    #[test]
    fn test_chain_link_broken() {
        let mut e1 = make_event("");
        e1.hash = e1.compute_hash();

        let mut e2 = make_event("bad_hash");
        e2.hash = e2.compute_hash();

        assert!(!e2.verify_chain_link(Some(&e1)));
    }
}