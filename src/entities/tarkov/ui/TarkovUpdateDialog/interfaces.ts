import { Dialog } from '@kobalte/core';

import { TarkovDownloadProgress } from '../..';

export interface UpdateDialogProps extends Dialog.DialogRootProps {
  progress: TarkovDownloadProgress;
}
