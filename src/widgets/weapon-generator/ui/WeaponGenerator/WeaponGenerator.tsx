import { useTransContext } from '@mbarzda/solid-i18next';
import i18next from 'i18next';
import { Component, Show, createSignal } from 'solid-js';

import {
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui';

import { Weapon, generateWeapon } from '@/entities/tarkov';
import { WeaponData } from '@/entities/weapon';

import { useTarkovData } from '@/app';

import { WeaponGeneratorProps } from '.';

export const WeaponGenerator: Component<WeaponGeneratorProps> = (props) => {
  const [weapon, setWeapon] = createSignal<Weapon | null>(null);
  const [isGenerating, setIsGenerating] = createSignal<boolean>(false);
  const [currentLanguage, setCurrentLanguage] = createSignal<string>(
    i18next.language,
  );

  const [_, { changeLanguage }] = useTransContext();

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

  const onLanguageChange = (value: string) => {
    changeLanguage(value);
    setCurrentLanguage(value);
    updateData(value as 'en' | 'ru');
  };

  return (
    <div class='flex flex-1 flex-col gap-2' {...props}>
      <div class='flex divide-x-2'>
        <Button class='w-full rounded-none font-bold' onClick={updateWeapon}>
          Generate
        </Button>
        <Button
          class='min-w-max rounded-none font-bold'
          onClick={() => updateData(i18next.language as 'en' | 'ru')}
        >
          Update data
        </Button>
        <Select
          value={currentLanguage()}
          options={['en', 'ru']}
          onChange={onLanguageChange}
          itemComponent={(props) => (
            <SelectItem item={props.item}>{props.item.rawValue}</SelectItem>
          )}
        >
          <SelectTrigger aria-label='Language' class='w-[64px]'>
            <SelectValue<string>>
              {(state) => state.selectedOption()}
            </SelectValue>
          </SelectTrigger>
          <SelectContent class='min-w-[64px]' />
        </Select>
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
