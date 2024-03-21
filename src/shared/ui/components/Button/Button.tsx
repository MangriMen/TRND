import type { Component } from 'solid-js';
import { splitProps } from 'solid-js';

import { cn } from '@/shared/lib';

import { ButtonProps, buttonVariants } from '.';

export const Button: Component<ButtonProps> = (props) => {
  const [, rest] = splitProps(props, ['variant', 'size', 'class']);
  return (
    <button
      class={cn(
        buttonVariants({ variant: props.variant, size: props.size }),
        props.class,
      )}
      {...rest}
    />
  );
};
