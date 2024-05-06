import { ComponentProps } from 'solid-js';

// eslint-disable-next-line boundaries/element-types
import { Weapon } from '@/entities/tarkov';

export interface WeaponDataProps extends ComponentProps<'div'> {
  data: Weapon;
}
