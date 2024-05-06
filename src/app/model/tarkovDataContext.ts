import { Accessor, createContext, useContext } from 'solid-js';

import { TarkovDownloadProgress } from '@/entities/tarkov';

export type TarkovDataContextProps = [
  Accessor<TarkovDownloadProgress>,
  Accessor<number>,
  {
    updateData: (lang: 'en' | 'ru') => void;
  },
];

export const TarkovDataContext = createContext<TarkovDataContextProps>();

export const useTarkovData = () => {
  const value = useContext(TarkovDataContext);
  if (value === undefined) {
    throw new Error('useMyContext must be used within a MyContext.Provider');
  }
  return value;
};
