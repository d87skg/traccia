use std::io::Read;
use crate::result::VerifyResult;

pub struct PackageVerifier;

impl PackageVerifier {
    pub fn new() -> Self {
        Self
    }

    /// 验证 .evidence ZIP 文件
    pub fn verify_file(&self, filepath: &str) -> VerifyResult {
        let mut result = VerifyResult::new();

        let file_data = match std::fs::read(filepath) {
            Ok(data) => data,
            Err(e) => {
                result.add_error("PKG-002", &format!("无法读取文件: {}", e));
                return result;
            }
        };

        self.verify_bytes(&file_data, &mut result);
        result
    }

    /// 验证 ZIP 字节数据
    pub fn verify_bytes(&self, data: &[u8], result: &mut VerifyResult) {
        let cursor = std::io::Cursor::new(data);
        let mut zip = match zip::ZipArchive::new(cursor) {
            Ok(z) => z,
            Err(e) => {
                result.add_error("PKG-001", &format!("不是有效的 ZIP: {}", e));
                return;
            }
        };

        // Step 1: 结构验证
        let required = ["manifest.json", "session.json", "events.jsonl", "signature.sig"];
        for file in &required {
            if zip.by_name(file).is_err() {
                result.add_error("ST-001", &format!("缺少必要文件: {}", file));
            }
        }

        if !result.valid {
            return;
        }

        // 加载内容
        let manifest: serde_json::Value = self.read_json_from_zip(&mut zip, "manifest.json", result);
        let session: serde_json::Value = self.read_json_from_zip(&mut zip, "session.json", result);
        let events = self.read_jsonl_from_zip(&mut zip, "events.jsonl", result);
        let evidences: Vec<serde_json::Value> =
            if zip.by_name("evidence.json").is_ok() {
                self.read_json_array_from_zip(&mut zip, "evidence.json", result)
            } else {
                Vec::new()
            };
        let attributions: Vec<serde_json::Value> =
            if zip.by_name("attributions.json").is_ok() {
                self.read_json_array_from_zip(&mut zip, "attributions.json", result)
            } else {
                Vec::new()
            };
        let signature = self.read_text_from_zip(&mut zip, "signature.sig", result);

        if !result.valid {
            return;
        }

        // Step 2: Session 验证
        self.verify_session(&session, result);

        // Step 3: Event Chain 验证
        self.verify_event_chain(&events, result);

        // Step 4: Evidence 验证
        self.verify_evidence(&evidences, &events, result);

        // Step 5: Signature 验证
        self.verify_signature(&manifest, &session, &events, &evidences, &attributions, &signature, result);
    }

    fn verify_session(&self, session: &serde_json::Value, result: &mut VerifyResult) {
        let required = ["session_id", "objective", "status"];
        for field in &required {
            if session.get(field).is_none() {
                result.add_error("SS-001", &format!("Session 缺少字段: {}", field));
            }
        }
    }

    fn verify_event_chain(&self, events: &[serde_json::Value], result: &mut VerifyResult) {
        if events.is_empty() {
            result.add_error("EV-001", "Event 列表为空");
            return;
        }

        let mut prev_hash = String::new();

        for (i, event) in events.iter().enumerate() {
            // 检查必填字段
            for field in &["event_id", "session_id", "event_type", "actor_id", "hash"] {
                if event.get(field).is_none() {
                    result.add_error("EV-002", &format!("Event[{}] 缺少字段: {}", i, field));
                }
            }

            let current_prev = event.get("prev_hash")
                .and_then(|v| v.as_str())
                .unwrap_or("");

            if i == 0 {
                // 创世Event
                if !current_prev.is_empty() {
                    result.add_error("EV-003", "创世Event的prev_hash必须为空");
                }
            } else {
                // 验证链上关系
                if current_prev != prev_hash {
                    result.add_error(
                        "EV-004",
                        &format!(
                            "Event[{}] HashChain断裂: 期望prev_hash={}...，实际={}...",
                            i,
                            &prev_hash[..16.min(prev_hash.len())],
                            &current_prev[..16.min(current_prev.len())]
                        )
                    );
                }
            }

            prev_hash = event.get("hash")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
        }
    }

    fn verify_evidence(
        &self,
        evidences: &[serde_json::Value],
        events: &[serde_json::Value],
        result: &mut VerifyResult,
    ) {
        let event_ids: Vec<&str> = events.iter()
            .filter_map(|e| e.get("event_id").and_then(|v| v.as_str()))
            .collect();

        for (i, ev) in evidences.iter().enumerate() {
            let event_id = ev.get("event_id").and_then(|v| v.as_str()).unwrap_or("");
            if !event_ids.contains(&event_id) {
                result.add_error("EVD-002", &format!("Evidence[{}] 关联的Event不存在: {}", i, event_id));
            }
        }
    }

    fn verify_signature(
        &self,
        manifest: &serde_json::Value,
        session: &serde_json::Value,
        events: &[serde_json::Value],
        evidences: &[serde_json::Value],
        attributions: &[serde_json::Value],
        signature: &str,
        result: &mut VerifyResult,
    ) {
        let content = serde_json::json!({
            "manifest": manifest,
            "session_id": session.get("session_id").unwrap_or(&serde_json::Value::Null),
            "session_objective": session.get("objective").unwrap_or(&serde_json::Value::Null),
            "session_status": session.get("status").unwrap_or(&serde_json::Value::Null),
            "events": events,
            "evidences": evidences,
            "attributions": attributions,
        });

        let content_str = serde_json::to_string(&content).unwrap_or_default();
        let expected = traccia_core::hash::sha256(&content_str);

        if expected != signature {
            result.add_error(
                "SIG-001",
                &format!(
                    "签名不匹配: 期望={}...，实际={}...",
                    &expected[..16],
                    &signature[..16.min(signature.len())]
                )
            );
        }
    }

    // ---- 辅助方法 ----

    fn read_json_from_zip(
        &self,
        zip: &mut zip::ZipArchive<std::io::Cursor<&[u8]>>,
        name: &str,
        result: &mut VerifyResult,
    ) -> serde_json::Value {
        match zip.by_name(name) {
            Ok(mut file) => {
                let mut buf = String::new();
                if file.read_to_string(&mut buf).is_err() {
                    result.add_error("IO-001", &format!("无法读取: {}", name));
                    return serde_json::Value::Null;
                }
                match serde_json::from_str(&buf) {
                    Ok(v) => v,
                    Err(e) => {
                        result.add_error("JSON-001", &format!("{} JSON解析错误: {}", name, e));
                        serde_json::Value::Null
                    }
                }
            }
            Err(_) => serde_json::Value::Null,
        }
    }

    fn read_jsonl_from_zip(
        &self,
        zip: &mut zip::ZipArchive<std::io::Cursor<&[u8]>>,
        name: &str,
        result: &mut VerifyResult,
    ) -> Vec<serde_json::Value> {
        match zip.by_name(name) {
            Ok(mut file) => {
                let mut buf = String::new();
                if file.read_to_string(&mut buf).is_err() {
                    result.add_error("IO-001", &format!("无法读取: {}", name));
                    return Vec::new();
                }
                buf.lines()
                    .filter(|l| !l.trim().is_empty())
                    .filter_map(|l| serde_json::from_str(l).ok())
                    .collect()
            }
            Err(_) => Vec::new(),
        }
    }

    fn read_json_array_from_zip(
        &self,
        zip: &mut zip::ZipArchive<std::io::Cursor<&[u8]>>,
        name: &str,
        result: &mut VerifyResult,
    ) -> Vec<serde_json::Value> {
        match zip.by_name(name) {
            Ok(mut file) => {
                let mut buf = String::new();
                if file.read_to_string(&mut buf).is_err() {
                    result.add_error("IO-001", &format!("无法读取: {}", name));
                    return Vec::new();
                }
                serde_json::from_str(&buf).unwrap_or_default()
            }
            Err(_) => Vec::new(),
        }
    }

    fn read_text_from_zip(
        &self,
        zip: &mut zip::ZipArchive<std::io::Cursor<&[u8]>>,
        name: &str,
        result: &mut VerifyResult,
    ) -> String {
        match zip.by_name(name) {
            Ok(mut file) => {
                let mut buf = String::new();
                if file.read_to_string(&mut buf).is_err() {
                    result.add_error("IO-001", &format!("无法读取: {}", name));
                }
                buf.trim().to_string()
            }
            Err(_) => String::new(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use traccia_package::{EvidencePackage, Manifest};

    #[test]
    fn test_verify_valid_package() {
        // 用 Rust 生成 package
        let e1 = traccia_event::EventBuilder::new("sess-1", "read_file", "agent_001")
            .payload(serde_json::json!({"file": "/data/q3.csv"}))
            .build();

        let mut pkg = EvidencePackage {
            manifest: Manifest::new(1, 0),
            session_id: "sess-1".to_string(),
            session_objective: "测试".to_string(),
            session_status: "completed".to_string(),
            events: vec![e1],
            evidences: vec![],
            attributions: vec![],
            signature: String::new(),
        };
        pkg.signature = pkg.compute_signature();

        let zip_bytes = pkg.export_zip().unwrap();

        let verifier = PackageVerifier::new();
        let mut result = VerifyResult::new();
        verifier.verify_bytes(&zip_bytes, &mut result);

        assert!(result.valid);
    }

    #[test]
    fn test_verify_tampered_package() {
        let e1 = traccia_event::EventBuilder::new("sess-1", "read_file", "agent_001")
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

        // 篡改后导出（签名不更新）
        pkg.session_objective = "tampered".to_string();
        let zip_bytes = pkg.export_zip().unwrap();

        let verifier = PackageVerifier::new();
        let mut result = VerifyResult::new();
        verifier.verify_bytes(&zip_bytes, &mut result);

        assert!(!result.valid);
        assert_eq!(result.status(), "TAMPERED");
    }
}

