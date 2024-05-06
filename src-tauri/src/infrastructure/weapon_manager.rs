use rand::Rng;

use crate::models::{
    tarkov::tarkov_dev_items,
    weapon::{Slot, Weapon},
};

pub fn get_random_mod(filters: &tarkov_dev_items::SlotFragmentFilters) -> String {
    let mut rng = rand::thread_rng();
    let random_mod = &filters.allowed_items[rng.gen_range(0..filters.allowed_items.len())];
    random_mod.as_ref().unwrap().id.to_owned()
}

pub fn generate_mods(
    data: &tarkov_dev_items::ResponseData,
    weapon: &tarkov_dev_items::TarkovDevItemsItemsPropertiesOnItemPropertiesWeapon,
) -> Vec<Slot> {
    let mod_ids = weapon
        .slots
        .as_ref()
        .unwrap()
        .into_iter()
        .map(|slot| get_random_mod(slot.as_ref().unwrap().filters.as_ref().unwrap()))
        .collect::<Vec<_>>();

    let items = data
        .items
        .iter()
        .filter(|item| mod_ids.iter().any(|id| &item.as_ref().unwrap().id == id))
        .collect::<Vec<_>>();

    items
        .iter()
        .map(|item| Slot {
            id: item.as_ref().unwrap().id.to_owned(),
            name: item.as_ref().unwrap().name.as_ref().unwrap().to_owned(),
            icon_link: item
                .as_ref()
                .unwrap()
                .icon_link
                .as_ref()
                .unwrap()
                .to_owned(),
            wiki_link: item
                .as_ref()
                .unwrap()
                .wiki_link
                .as_ref()
                .unwrap()
                .to_owned(),
        })
        .collect()
}

pub fn generate_new_weapon(data: &tarkov_dev_items::ResponseData) -> Weapon {
    let items_iter = data.items.iter();

    let weapons = items_iter
        .filter(|item| {
            item.as_ref()
                .unwrap()
                .types
                .iter()
                .any(|t| matches!(t.as_ref().unwrap(), tarkov_dev_items::ItemType::gun))
        })
        .collect::<Vec<_>>();

    let mut rng = rand::thread_rng();
    let weapon = weapons[rng.gen_range(0..weapons.len())].as_ref().unwrap();
    let properties_value = serde_json::to_value(&weapon.properties).unwrap();

    let mods = generate_mods(
        data,
        &serde_json::from_value::<
            tarkov_dev_items::TarkovDevItemsItemsPropertiesOnItemPropertiesWeapon,
        >(properties_value)
        .unwrap(),
    );

    Weapon {
        name: weapon.name.as_ref().unwrap().to_owned(),
        icon_link: weapon.icon_link.as_ref().unwrap().to_owned(),
        wiki_link: weapon.wiki_link.as_ref().unwrap().to_owned(),
        slots: mods,
    }
}
