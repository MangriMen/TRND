use crate::models::tarkov::tarkov_dev_items::Variables;
use graphql_client::QueryBody;
use reqwest;

pub async fn run_tarkov_query(
    body: &QueryBody<Variables>,
) -> Result<reqwest::Response, reqwest::Error> {
    reqwest::Client::new()
        .post("https://api.tarkov.dev/graphql")
        .json(&body)
        .send()
        .await
}
