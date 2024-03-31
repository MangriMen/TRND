import { Component, createComputed, createSignal } from 'solid-js';

import {
  TarkovDownloadProgress,
  TarkovUpdateDialog,
  listenProgress,
  updateTarkovData,
} from '@/entities/tarkov';

export const TarkovUpdateObserver: Component = () => {
  const [progress, setProgress] = createSignal<TarkovDownloadProgress>({
    current_size: 0,
    full_size: 0,
  });
  const [progressPercent, setProgressPercent] = createSignal(0);

  const updateProgress = (payload: TarkovDownloadProgress) => {
    const progressPercent = (payload.current_size / payload.full_size) * 100;

    setProgress(payload);
    setProgressPercent(progressPercent);
  };

  createComputed(() => {
    updateTarkovData();
    listenProgress((event) => updateProgress(event.payload));
  });

  return (
    <TarkovUpdateDialog progress={progress()} open={progressPercent() < 100} />
  );
};
