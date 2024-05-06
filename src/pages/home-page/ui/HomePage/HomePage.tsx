import { Component } from 'solid-js';

import { WeaponGenerator } from '@/widgets/weapon-generator';

export const HomePage: Component = () => {
  return (
    <div class='flex h-full min-h-screen flex-col'>
      <WeaponGenerator />
    </div>
  );
};
