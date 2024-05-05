import { invoke } from '@tauri-apps/api';

export const updateTarkovData = (language: 'ru' | 'en') =>
  invoke('update_data', { language });
