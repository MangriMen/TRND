import { request } from 'graphql-request';

export const runTarkovQuery = async (query: string) =>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  request<Record<string, any>>('https://api.tarkov.dev/graphql', query)
    .then((res) => res)
    .catch((e) => e);
