use chrono::Utc;

pub fn now() -> String {
    Utc::now().to_rfc3339()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_now_is_iso8601() {
        let t = now();
        assert!(t.contains("T"));
        assert!(t.contains("+") || t.contains("Z"));
    }
}