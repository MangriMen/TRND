import './app.css';

import {
  ColorModeProvider,
  ColorModeScript,
  cookieStorageManager,
} from '@kobalte/core';
import { TransProvider } from '@mbarzda/solid-i18next';

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
        <TransProvider
          lng='en'
          options={{
            debug: true,
            interpolation: {
              escapeValue: true,
            },
            fallbackLng: 'en',
            resources: {
              en: {
                translation: {},
              },
              ru: {
                translation: {},
              },
            },
          }}
        >
          <TarkovDataContextProvider>
            <AppRouter />
            <TarkovDataContextUpdateDialog />
          </TarkovDataContextProvider>
        </TransProvider>
      </ColorModeProvider>
    </>
  );
};
