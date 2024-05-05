import { Component, For, splitProps } from 'solid-js';

import { cn } from '@/shared/lib';

import { ItemCard } from '../ItemCard';

import { WeaponDataProps } from '.';

export const WeaponData: Component<WeaponDataProps> = (props) => {
  const [local, rest] = splitProps(props, ['class', 'data']);

  return (
    <div class={cn('flex flex-col gap-4', local.class)} {...rest}>
      <ItemCard item={local.data} />
      <hr />
      <For each={local.data.slots}>{(slot) => <ItemCard item={slot} />}</For>
    </div>
  );
};
