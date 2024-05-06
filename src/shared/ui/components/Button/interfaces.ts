import { VariantProps } from 'class-variance-authority';
import { ComponentProps } from 'solid-js';

import { buttonVariants } from '.';

export interface ButtonProps
  extends ComponentProps<'button'>,
    VariantProps<typeof buttonVariants> {}
