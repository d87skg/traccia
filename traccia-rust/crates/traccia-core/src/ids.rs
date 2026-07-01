use uuid::Uuid;

pub fn new_id() -> String {
    Uuid::new_v4().to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_id_is_not_empty() {
        let id = new_id();
        assert!(!id.is_empty());
    }

    #[test]
    fn test_new_id_is_unique() {
        let id1 = new_id();
        let id2 = new_id();
        assert_ne!(id1, id2);
    }
}