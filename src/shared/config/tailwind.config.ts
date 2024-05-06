import { Config } from 'tailwindcss/types/config';

export const tailwindConfig: Config = {
  darkMode: ['class', '[data-kb-theme="dark"]'],
  content: ['./src/**/*.{html,js,jsx,md,mdx,ts,tsx}'],
  presets: [require('./ui.preset.js')],
};
