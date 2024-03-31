import { invoke } from '@tauri-apps/api';

export const updateTarkovData = () => invoke('update_data');
