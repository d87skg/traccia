use crate::models::{Actor, ResponsibilityRecord};

/// AttributionProvider：责任归属提供者（抽象 trait）
///
/// Traccia 定义此接口，不依赖任何特定实现。
/// AES 只是其中一种实现。
pub trait AttributionProvider {
    fn resolve_session(&self, session_id: &str) -> Option<ResponsibilityRecord>;
    fn resolve_event(&self, event_id: &str) -> Option<ResponsibilityRecord>;
}

/// AESProvider：AES 责任归属提供者（Stub 实现）
pub struct AESProvider {
    #[allow(dead_code)]
    endpoint: String,
}

impl AESProvider {
    pub fn new(endpoint: &str) -> Self {
        Self {
            endpoint: endpoint.to_string(),
        }
    }
}

impl AttributionProvider for AESProvider {
    fn resolve_session(&self, _session_id: &str) -> Option<ResponsibilityRecord> {
        // Stub: 模拟 AES 响应
        Some(
            ResponsibilityRecord::new(_session_id, "session", Actor::new("agent_001", "agent"))
                .with_supervisor(Actor::new("operator_001", "human"))
                .with_approver(Actor::new("ceo_001", "human"))
                .with_policy("AES-RISK-001")
                .with_risk("medium")
        )
    }

    fn resolve_event(&self, _event_id: &str) -> Option<ResponsibilityRecord> {
        // Stub: 模拟 AES 响应
        Some(
            ResponsibilityRecord::new(_event_id, "event", Actor::new("agent_001", "agent"))
                .with_risk("low")
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aes_provider_resolve_session() {
        let provider = AESProvider::new("http://localhost:8080");
        let record = provider.resolve_session("sess-1").unwrap();

        assert_eq!(record.executor.id, "agent_001");
        assert!(record.supervisor.is_some());
        assert!(record.approver.is_some());
        assert_eq!(record.risk_level, "medium");
    }

    #[test]
    fn test_aes_provider_resolve_event() {
        let provider = AESProvider::new("http://localhost:8080");
        let record = provider.resolve_event("evt-1").unwrap();

        assert_eq!(record.subject_type, "event");
        assert_eq!(record.risk_level, "low");
    }
}
