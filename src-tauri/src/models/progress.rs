use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Progress {
    pub current_size: u64,
    pub full_size: u64,
}
