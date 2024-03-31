// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use trnd::{
    commands::tarkov_data::{__cmd__update_data, update_data},
    utilities::tauri::get_app_dir,
};

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let app_dir = get_app_dir(&app.handle());
            let _ = std::fs::create_dir_all(&app_dir);

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![update_data])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
