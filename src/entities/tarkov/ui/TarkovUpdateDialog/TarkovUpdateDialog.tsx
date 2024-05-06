import { Component, createMemo, splitProps } from 'solid-js';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Progress,
} from '@/shared/ui';

import { UpdateDialogProps } from '.';

export const TarkovUpdateDialog: Component<UpdateDialogProps> = (props) => {
  const [local, rest] = splitProps(props, ['children', 'progress']);

  const progressPercent = createMemo(
    () => (local.progress.current_size / local.progress.full_size) * 100 || 0,
  );

  return (
    <Dialog defaultOpen modal preventScroll {...rest}>
      <DialogContent closable={false}>
        <DialogHeader>
          <DialogTitle>Updating data</DialogTitle>
        </DialogHeader>
        <div class='flex flex-col'>
          <Progress
            class='w-full'
            value={progressPercent()}
            minValue={0}
            maxValue={100}
          />
          <span class='self-end'>
            {(local.progress.current_size / 1024 / 1024).toFixed(2)}/
            {(local.progress.full_size / 1024 / 1024).toFixed(2)} Мб
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
};
