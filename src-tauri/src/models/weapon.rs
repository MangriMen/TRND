use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Weapon {
    pub name: String,
    pub icon_link: String,
    pub wiki_link: String,
    pub slots: Vec<Slot>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Slot {
    pub id: String,
    pub name: String,
    pub icon_link: String,
    pub wiki_link: String,
}
