use graphql_client::GraphQLQuery;
use serde::{Deserialize, Serialize};

#[derive(GraphQLQuery)]
#[graphql(
    query_path = "src/assets/tarkov_dev_items.graphql",
    schema_path = "src/assets/tarkov_query.json",
    response_derives = "Serialize,Deserialize,PartialEq"
)]
pub struct TarkovDevItems;

#[derive(Serialize, Deserialize)]
pub struct TarkovDevItemsFile {
    pub data: tarkov_dev_items::ResponseData,
}
