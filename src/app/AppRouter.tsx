import './app.css';

import { gql } from 'graphql-request';
import { createResource } from 'solid-js';

import { Button } from '@/shared/ui';

import { runTarkovQuery } from '@/entities/tarkov';

export const AppRouter = () => {
  const [data] = createResource(() =>
    runTarkovQuery(gql`
      {
        items(name: "m855a1") {
          id
          name
          shortName
        }
      }
    `),
  );

  return (
    <div>
      <div>{JSON.stringify(data())}</div>
      <Button>Hello</Button>
    </div>
  );
};
