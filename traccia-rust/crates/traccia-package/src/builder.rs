use crate::manifest::{EvidencePackage, Manifest};
use traccia_event::Event;
use traccia_evidence::Evidence;

pub struct PackageBuilder {
    session_id: String,
    session_objective: String,
    session_status: String,
    events: Vec<Event>,
    evidences: Vec<Evidence>,
    attributions: Vec<serde_json::Value>,
}

impl PackageBuilder {
    pub fn new(session_id: &str, objective: &str) -> Self {
        Self {
            session_id: session_id.to_string(),
            session_objective: objective.to_string(),
            session_status: "running".to_string(),
            events: Vec::new(),
            evidences: Vec::new(),
            attributions: Vec::new(),
        }
    }

    pub fn status(mut self, status: &str) -> Self {
        self.session_status = status.to_string();
        self
    }

    pub fn add_event(mut self, event: Event) -> Self {
        self.events.push(event);
        self
    }

    pub fn add_evidence(mut self, evidence: Evidence) -> Self {
        self.evidences.push(evidence);
        self
    }

    pub fn add_attribution(mut self, attribution: serde_json::Value) -> Self {
        self.attributions.push(attribution);
        self
    }

    pub fn build(self) -> EvidencePackage {
        let events_count = self.events.len() as u64;
        let evidences_count = self.evidences.len() as u64;

        let mut pkg = EvidencePackage {
            manifest: Manifest::new(events_count, evidences_count),
            session_id: self.session_id,
            session_objective: self.session_objective,
            session_status: self.session_status,
            events: self.events,
            evidences: self.evidences,
            attributions: self.attributions,
            signature: String::new(),
        };

        pkg.signature = pkg.compute_signature();
        pkg
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use traccia_event::EventBuilder;
    use traccia_evidence::{Evidence, EvidenceType};

    #[test]
    fn test_package_builder() {
        let e1 = EventBuilder::new("sess-1", "read_file", "agent_001")
            .build();

        let ev1 = Evidence::new(
            &e1.event_id,
            EvidenceType::FileHash,
            "hash123",
            "file:///evd_001.bin",
        );

        let pkg = PackageBuilder::new("sess-1", "生成Q3报告")
            .status("completed")
            .add_event(e1)
            .add_evidence(ev1)
            .build();

        assert_eq!(pkg.manifest.events_count, 1);
        assert_eq!(pkg.manifest.evidences_count, 1);
        assert!(pkg.verify_signature());
    }
}
