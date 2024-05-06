import { Component } from 'solid-js';

import { TarkovUpdateDialog } from '@/entities/tarkov';

import { useTarkovData } from '@/app';

export const TarkovDataContextUpdateDialog: Component = () => {
  const [progress, progressPercent] = useTarkovData();

  return (
    <TarkovUpdateDialog progress={progress()} open={progressPercent() < 100} />
  );
};
