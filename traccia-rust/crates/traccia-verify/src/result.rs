use std::fmt;

#[derive(Debug, Clone)]
pub struct VerifyError {
    pub code: String,
    pub message: String,
}

impl VerifyError {
    pub fn new(code: &str, message: &str) -> Self {
        Self {
            code: code.to_string(),
            message: message.to_string(),
        }
    }
}

impl fmt::Display for VerifyError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

#[derive(Debug)]
pub struct VerifyResult {
    pub valid: bool,
    pub errors: Vec<VerifyError>,
    pub warnings: Vec<String>,
}

impl VerifyResult {
    pub fn new() -> Self {
        Self {
            valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
        }
    }

    pub fn add_error(&mut self, code: &str, message: &str) {
        self.valid = false;
        self.errors.push(VerifyError::new(code, message));
    }

    pub fn add_warning(&mut self, message: &str) {
        self.warnings.push(message.to_string());
    }

    pub fn status(&self) -> &str {
        if self.valid { "VALID" } else { "TAMPERED" }
    }

    pub fn report(&self) -> String {
        let mut lines = Vec::new();
        lines.push(format!("Status: {}", self.status()));
        lines.push(format!("Errors: {}", self.errors.len()));
        for e in &self.errors {
            lines.push(format!("  {}", e));
        }
        lines.push(format!("Warnings: {}", self.warnings.len()));
        for w in &self.warnings {
            lines.push(format!("  {}", w));
        }
        lines.join("\n")
    }
}

impl Default for VerifyResult {
    fn default() -> Self {
        Self::new()
    }
}
