use std::{fs::File, io::Write};

use crate::{
    infrastructure::api::tarkov_api::run_tarkov_query,
    models::{
        progress::Progress,
        tarkov::{
            tarkov_dev_items::{self},
            TarkovDevItems,
        },
    },
    utilities::tauri::get_app_dir,
};
use graphql_client::GraphQLQuery;
use tauri::Manager;

#[tauri::command]
pub async fn update_data(app_handle: tauri::AppHandle, language: String) {
    let app_dir = get_app_dir(&app_handle);

    let lang = match language.as_str() {
        "ru" => tarkov_dev_items::LanguageCode::ru,
        "en" | _ => tarkov_dev_items::LanguageCode::en,
    };

    let variables = tarkov_dev_items::Variables { lang };

    let request_body = TarkovDevItems::build_query(variables);

    let mut response = run_tarkov_query(&request_body).await.unwrap();

    if response.status().is_success() {
        let mut file = File::create(app_dir.join("tarkov_dev_items.json")).unwrap();

        while let Some(chunk) = response.chunk().await.unwrap() {
            let _ = file.write_all(&chunk);

            let file_size = file.metadata().unwrap().len();
            let content_length = response.content_length().unwrap_or_else(|| 0);

            app_handle
                .emit_all(
                    "download-progress",
                    Progress {
                        current_size: file_size,
                        full_size: file_size + content_length,
                    },
                )
                .unwrap();
        }
    }
}
