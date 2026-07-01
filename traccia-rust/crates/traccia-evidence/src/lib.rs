use serde::{Deserialize, Serialize};
use traccia_core::ids::new_id;
use traccia_core::time::now;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EvidenceType {
    #[serde(rename = "file_hash")]
    FileHash,
    #[serde(rename = "api_response")]
    ApiResponse,
    #[serde(rename = "shell_output")]
    ShellOutput,
    #[serde(rename = "screenshot")]
    Screenshot,
    #[serde(rename = "custom")]
    Custom,
}

impl EvidenceType {
    pub fn as_str(&self) -> &str {
        match self {
            EvidenceType::FileHash => "file_hash",
            EvidenceType::ApiResponse => "api_response",
            EvidenceType::ShellOutput => "shell_output",
            EvidenceType::Screenshot => "screenshot",
            EvidenceType::Custom => "custom",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "file_hash" => Some(EvidenceType::FileHash),
            "api_response" => Some(EvidenceType::ApiResponse),
            "shell_output" => Some(EvidenceType::ShellOutput),
            "screenshot" => Some(EvidenceType::Screenshot),
            _ => Some(EvidenceType::Custom),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub evidence_id: String,
    pub event_id: String,
    #[serde(rename = "type")]
    pub evidence_type: EvidenceType,
    pub sha256: String,
    pub storage_uri: String,
    pub created_at: String,
}

impl Evidence {
    pub fn new(
        event_id: &str,
        evidence_type: EvidenceType,
        sha256_hash: &str,
        storage_uri: &str,
    ) -> Self {
        Self {
            evidence_id: new_id(),
            event_id: event_id.to_string(),
            evidence_type,
            sha256: sha256_hash.to_string(),
            storage_uri: storage_uri.to_string(),
            created_at: now(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_evidence() {
        let ev = Evidence::new(
            "evt-001",
            EvidenceType::FileHash,
            "abc123def456",
            "file:///evidence/evd_001.bin",
        );

        assert_eq!(ev.event_id, "evt-001");
        assert_eq!(ev.evidence_type, EvidenceType::FileHash);
        assert!(!ev.evidence_id.is_empty());
        assert!(!ev.created_at.is_empty());
    }

    #[test]
    fn test_evidence_type_from_str() {
        assert_eq!(
            EvidenceType::from_str("file_hash"),
            Some(EvidenceType::FileHash)
        );
        assert_eq!(
            EvidenceType::from_str("unknown_type"),
            Some(EvidenceType::Custom)
        );
    }

    #[test]
    fn test_evidence_type_as_str() {
        assert_eq!(EvidenceType::ApiResponse.as_str(), "api_response");
    }

    #[test]
    fn test_evidence_serialization() {
        let ev = Evidence::new(
            "evt-001",
            EvidenceType::Screenshot,
            "hash123",
            "file:///ss.png",
        );

        let json = serde_json::to_string(&ev).unwrap();
        let restored: Evidence = serde_json::from_str(&json).unwrap();

        assert_eq!(ev.evidence_id, restored.evidence_id);
        assert_eq!(ev.evidence_type, restored.evidence_type);
    }
}
