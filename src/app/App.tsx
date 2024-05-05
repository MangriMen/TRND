import './app.css';

import {
  ColorModeProvider,
  ColorModeScript,
  cookieStorageManager,
} from '@kobalte/core';

import { TarkovDataContextUpdateDialog } from '@/widgets/tarkov-update-observer';

import { AppRouter, TarkovDataContextProvider } from '.';

export const App = () => {
  return (
    <>
      <ColorModeScript
        initialColorMode='dark'
        storageType={cookieStorageManager.type}
      />
      <ColorModeProvider storageManager={cookieStorageManager}>
        <TarkovDataContextProvider>
          <AppRouter />
          <TarkovDataContextUpdateDialog />
        </TarkovDataContextProvider>
      </ColorModeProvider>
    </>
  );
};
