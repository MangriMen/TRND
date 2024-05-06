import { listen } from '@tauri-apps/api/event';

import { TarkovDownloadProgress } from '../model';

export const listenProgress = (
  callback: Parameters<typeof listen<TarkovDownloadProgress>>[1],
) => listen<TarkovDownloadProgress>('download-progress', callback);
