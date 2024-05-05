import { open } from '@tauri-apps/api/shell';
import { Component, splitProps } from 'solid-js';

import { ItemCardProps } from '.';

export const ItemCard: Component<ItemCardProps> = (props) => {
  const [local, rest] = splitProps(props, ['item']);

  return (
    <div class='flex items-center gap-2' {...rest}>
      <img width={64} height={64} src={local.item.icon_link} />
      <button onClick={() => open(local.item.wiki_link)}>
        {local.item.name}
      </button>
    </div>
  );
};
