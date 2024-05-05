import { Component, Show, createSignal } from 'solid-js';

import { Button } from '@/shared/ui';

import { Weapon, generateWeapon } from '@/entities/tarkov';
import { WeaponData } from '@/entities/weapon';

import { useTarkovData } from '@/app';

import { WeaponGeneratorProps } from '.';

export const WeaponGenerator: Component<WeaponGeneratorProps> = (props) => {
  const [weapon, setWeapon] = createSignal<Weapon | null>(null);
  const [isGenerating, setIsGenerating] = createSignal<boolean>(false);

  const [_1, _2, { updateData }] = useTarkovData();

  const updateWeapon = async () => {
    setIsGenerating(true);
    setWeapon(
      await generateWeapon().then((res) => {
        setIsGenerating(false);
        return res;
      }),
    );
  };

  return (
    <div class='flex flex-1 flex-col gap-2' {...props}>
      <div class='flex divide-x-2'>
        <Button class='w-full rounded-none font-bold' onClick={updateWeapon}>
          Generate
        </Button>
        <Button class='min-w-max rounded-none font-bold' onClick={updateData}>
          Update data
        </Button>
      </div>
      <div class='flex flex-1 p-2'>
        <Show
          when={weapon() !== null}
          fallback={
            <div class='flex flex-1 items-center justify-center'>
              <Show
                when={!isGenerating()}
                fallback={<span>Generating...</span>}
              >
                <span>Press generate to start</span>
              </Show>
            </div>
          }
        >
          <WeaponData class='flex-1' data={weapon()!} />
        </Show>
      </div>
    </div>
  );
};
