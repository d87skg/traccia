use serde::{Deserialize, Serialize};
use traccia_core::time::now;
use traccia_event::Event;
use traccia_evidence::Evidence;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    pub traccia_version: String,
    pub package_version: String,
    pub created_at: String,
    pub events_count: u64,
    pub evidences_count: u64,
}

impl Manifest {
    pub fn new(events_count: u64, evidences_count: u64) -> Self {
        Self {
            traccia_version: "1.0.0".to_string(),
            package_version: "1.0.0".to_string(),
            created_at: now(),
            events_count,
            evidences_count,
        }
    }
}

/// EvidencePackage：一个可独立验证的完整执行证明文件。
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidencePackage {
    pub manifest: Manifest,
    pub session_id: String,
    pub session_objective: String,
    pub session_status: String,
    pub events: Vec<Event>,
    pub evidences: Vec<Evidence>,
    pub attributions: Vec<serde_json::Value>,
    pub signature: String,
}

impl EvidencePackage {
    /// 生成签名（SHA-256 简化实现）
    pub fn compute_signature(&self) -> String {
        let content = serde_json::json!({
            "manifest": self.manifest,
            "session_id": self.session_id,
            "session_objective": self.session_objective,
            "session_status": self.session_status,
            "events": self.events,
            "evidences": self.evidences,
            "attributions": self.attributions,
        });
        let content_str = serde_json::to_string(&content).unwrap_or_default();
        traccia_core::hash::sha256(&content_str)
    }

    /// 验证签名
    pub fn verify_signature(&self) -> bool {
        self.compute_signature() == self.signature
    }

    /// 导出为 .evidence ZIP 字节
    pub fn export_zip(&self) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        use std::io::Write;
        use zip::write::FileOptions;

        let mut buffer = Vec::new();
        {
            let mut zip_writer = zip::ZipWriter::new(std::io::Cursor::new(&mut buffer));
            let options: FileOptions<()> = FileOptions::default()
                .compression_method(zip::CompressionMethod::Deflated);

            // manifest.json
            zip_writer.start_file("manifest.json", options)?;
            zip_writer.write_all(
                serde_json::to_string_pretty(&self.manifest)?.as_bytes()
            )?;

            // session.json
            let session = serde_json::json!({
                "session_id": self.session_id,
                "objective": self.session_objective,
                "status": self.session_status,
            });
            zip_writer.start_file("session.json", options)?;
            zip_writer.write_all(
                serde_json::to_string_pretty(&session)?.as_bytes()
            )?;

            // events.jsonl
            let events_lines: Vec<String> = self.events.iter()
                .map(|e| serde_json::to_string(e).unwrap_or_default())
                .collect();
            zip_writer.start_file("events.jsonl", options)?;
            zip_writer.write_all(events_lines.join("\n").as_bytes())?;

            // evidence.json
            if !self.evidences.is_empty() {
                let ev_json = serde_json::to_string_pretty(&self.evidences)?;
                zip_writer.start_file("evidence.json", options)?;
                zip_writer.write_all(ev_json.as_bytes())?;
            }

            // attributions.json
            if !self.attributions.is_empty() {
                let attr_json = serde_json::to_string_pretty(&self.attributions)?;
                zip_writer.start_file("attributions.json", options)?;
                zip_writer.write_all(attr_json.as_bytes())?;
            }

            // signature.sig
            zip_writer.start_file("signature.sig", options)?;
            zip_writer.write_all(self.signature.as_bytes())?;

            zip_writer.finish()?;
        }

        Ok(buffer)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use traccia_event::EventBuilder;
    use traccia_evidence::{Evidence, EvidenceType};

    #[test]
    fn test_package_creation() {
        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .payload(serde_json::json!({"file": "/data/q3.csv"}))
            .build();

        let ev1 = Evidence::new(
            &e1.event_id,
            EvidenceType::FileHash,
            "abc123",
            "file:///evidence/evd_001.bin",
        );

        let mut pkg = EvidencePackage {
            manifest: Manifest::new(1, 1),
            session_id: "sess-1".to_string(),
            session_objective: "生成Q3报告".to_string(),
            session_status: "completed".to_string(),
            events: vec![e1],
            evidences: vec![ev1],
            attributions: vec![],
            signature: String::new(),
        };

        pkg.signature = pkg.compute_signature();

        assert!(pkg.verify_signature());
    }

    #[test]
    fn test_package_export_zip() {
        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .build();

        let mut pkg = EvidencePackage {
            manifest: Manifest::new(1, 0),
            session_id: "sess-1".to_string(),
            session_objective: "test".to_string(),
            session_status: "completed".to_string(),
            events: vec![e1],
            evidences: vec![],
            attributions: vec![],
            signature: String::new(),
        };
        pkg.signature = pkg.compute_signature();

        let zip_bytes = pkg.export_zip().unwrap();
        assert!(!zip_bytes.is_empty());
    }

    #[test]
    fn test_signature_tamper_detection() {
        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .build();

        let mut pkg = EvidencePackage {
            manifest: Manifest::new(1, 0),
            session_id: "sess-1".to_string(),
            session_objective: "original".to_string(),
            session_status: "completed".to_string(),
            events: vec![e1],
            evidences: vec![],
            attributions: vec![],
            signature: String::new(),
        };
        pkg.signature = pkg.compute_signature();

        // 篡改
        pkg.session_objective = "tampered".to_string();

        assert!(!pkg.verify_signature());
    }
}
