use serde::{Deserialize, Serialize};
use traccia_core::ids::new_id;
use traccia_core::time::now;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Actor {
    pub id: String,
    #[serde(rename = "type")]
    pub actor_type: String,  // "agent" | "human" | "workflow" | "committee"
}

impl Actor {
    pub fn new(id: &str, actor_type: &str) -> Self {
        Self {
            id: id.to_string(),
            actor_type: actor_type.to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResponsibilityRecord {
    pub record_id: String,
    pub subject_id: String,
    pub subject_type: String,  // "session" | "event"
    pub executor: Actor,
    pub supervisor: Option<Actor>,
    pub approver: Option<Actor>,
    pub policy_id: Option<String>,
    pub risk_level: String,
    pub resolved_at: String,
}

impl ResponsibilityRecord {
    pub fn new(subject_id: &str, subject_type: &str, executor: Actor) -> Self {
        Self {
            record_id: new_id(),
            subject_id: subject_id.to_string(),
            subject_type: subject_type.to_string(),
            executor,
            supervisor: None,
            approver: None,
            policy_id: None,
            risk_level: "medium".to_string(),
            resolved_at: now(),
        }
    }

    pub fn with_supervisor(mut self, actor: Actor) -> Self {
        self.supervisor = Some(actor);
        self
    }

    pub fn with_approver(mut self, actor: Actor) -> Self {
        self.approver = Some(actor);
        self
    }

    pub fn with_policy(mut self, policy_id: &str) -> Self {
        self.policy_id = Some(policy_id.to_string());
        self
    }

    pub fn with_risk(mut self, risk_level: &str) -> Self {
        self.risk_level = risk_level.to_string();
        self
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResponsibilityLink {
    pub actor: Actor,
    pub role: String,  // "executor" | "supervisor" | "approver"
    pub timestamp: String,
    pub comment: Option<String>,
}

impl ResponsibilityLink {
    pub fn new(actor: Actor, role: &str) -> Self {
        Self {
            actor,
            role: role.to_string(),
            timestamp: now(),
            comment: None,
        }
    }

    pub fn with_comment(mut self, comment: &str) -> Self {
        self.comment = Some(comment.to_string());
        self
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResponsibilityChain {
    pub chain_id: String,
    pub session_id: String,
    pub links: Vec<ResponsibilityLink>,
}

impl ResponsibilityChain {
    pub fn new(session_id: &str) -> Self {
        Self {
            chain_id: new_id(),
            session_id: session_id.to_string(),
            links: Vec::new(),
        }
    }

    pub fn add_link(&mut self, link: ResponsibilityLink) {
        self.links.push(link);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_actor_creation() {
        let actor = Actor::new("agent_001", "agent");
        assert_eq!(actor.id, "agent_001");
        assert_eq!(actor.actor_type, "agent");
    }

    #[test]
    fn test_responsibility_record() {
        let record = ResponsibilityRecord::new(
            "sess-1",
            "session",
            Actor::new("agent_001", "agent"),
        )
        .with_supervisor(Actor::new("human_001", "human"))
        .with_approver(Actor::new("ceo_001", "human"))
        .with_policy("AES-RISK-001")
        .with_risk("high");

        assert_eq!(record.risk_level, "high");
        assert!(record.supervisor.is_some());
        assert!(record.approver.is_some());
    }

    #[test]
    fn test_responsibility_chain() {
        let mut chain = ResponsibilityChain::new("sess-1");
        chain.add_link(
            ResponsibilityLink::new(Actor::new("agent_001", "agent"), "executor")
                .with_comment("执行生成报告")
        );
        chain.add_link(
            ResponsibilityLink::new(Actor::new("human_001", "human"), "approver")
                .with_comment("最终审批")
        );

        assert_eq!(chain.links.len(), 2);
        assert_eq!(chain.links[0].role, "executor");
        assert_eq!(chain.links[1].role, "approver");
    }
}
