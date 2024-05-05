import { Component, JSX, createComputed, createSignal } from 'solid-js';

import {
  TarkovDownloadProgress,
  listenProgress,
  updateTarkovData,
} from '@/entities/tarkov';

import { TarkovDataContext, TarkovDataContextProps } from '@/app';

export const TarkovDataContextProvider: Component<{
  children?: JSX.Element;
}> = (props) => {
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

  const updateData = () => {
    updateTarkovData();
    listenProgress((event) => updateProgress(event.payload));
  };

  const tarkovDataContextValue: TarkovDataContextProps = [
    progress,
    progressPercent,
    {
      updateData,
    },
  ];

  createComputed(() => {
    updateData();
  });

  return (
    <TarkovDataContext.Provider value={tarkovDataContextValue}>
      {props.children}
    </TarkovDataContext.Provider>
  );
};
