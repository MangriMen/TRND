import { ComponentProps } from 'solid-js';

// eslint-disable-next-line boundaries/element-types
import { Slot, Weapon } from '@/entities/tarkov';

export interface ItemCardProps extends ComponentProps<'div'> {
  item: Weapon | Slot;
}
