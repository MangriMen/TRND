import './app.css';

import {
  ColorModeProvider,
  ColorModeScript,
  cookieStorageManager,
} from '@kobalte/core';

import { TarkovUpdateObserver } from '@/widgets/tarkov-update-observer';

import { AppRouter } from '.';

export const App = () => {
  return (
    <>
      <ColorModeScript storageType={cookieStorageManager.type} />
      <ColorModeProvider storageManager={cookieStorageManager}>
        <TarkovUpdateObserver />
        <AppRouter />
      </ColorModeProvider>
    </>
  );
};
