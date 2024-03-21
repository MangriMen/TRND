/* @refresh reload */
import { render } from 'solid-js/web';
import { AppRouter } from './app';

render(() => <AppRouter />, document.getElementById('root') as HTMLElement);
