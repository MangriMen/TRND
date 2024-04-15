import { Component, createSignal } from 'solid-js';

import { Button } from '@/shared/ui';

import { Weapon, generateWeapon } from '@/entities/tarkov';
import { WeaponData } from '@/entities/weapon';

import { WeaponGeneratorProps } from '.';

export const WeaponGenerator: Component<WeaponGeneratorProps> = (props) => {
  const [weapon, setWeapon] = createSignal<Weapon>({
    name: 'Start',
    slots: [],
  });

  const updateWeapon = async () => {
    setWeapon(await generateWeapon());
  };

  return (
    <div class='flex flex-1 flex-col' {...props}>
      <WeaponData class='flex-1' data={weapon()} />
      <Button class='w-full self-end' onClick={updateWeapon}>
        Generate
      </Button>
    </div>
  );
};
