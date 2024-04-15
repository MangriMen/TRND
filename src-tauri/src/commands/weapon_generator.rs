use std::fs;

use crate::{
    infrastructure::weapon_manager::generate_new_weapon,
    models::{tarkov::TarkovDevItemsFile, weapon::Weapon},
    utilities::tauri::get_app_dir,
};

#[tauri::command]
pub fn generate_weapon(app_handle: tauri::AppHandle) -> Weapon {
    let app_dir = get_app_dir(&app_handle);

    let data = {
        let res =
            fs::read_to_string(app_dir.join("tarkov_dev_items.json")).expect("Can't read file");
        serde_json::from_str::<TarkovDevItemsFile>(&res).unwrap()
    };

    generate_new_weapon(&data.data)
}
