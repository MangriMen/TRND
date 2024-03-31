use graphql_client::GraphQLQuery;

#[derive(GraphQLQuery)]
#[graphql(
    query_path = "src/assets/tarkov_dev_items.graphql",
    schema_path = "src/assets/tarkov_query.json"
)]
pub struct TarkovDevItems;
