import { Component, splitProps } from 'solid-js';

import { WeaponDataProps } from '.';

export const WeaponData: Component<WeaponDataProps> = (props) => {
  const [local, rest] = splitProps(props, ['data']);

  return (
    <div {...rest}>
      <div />
      {JSON.stringify(local.data)}
    </div>
  );
};
