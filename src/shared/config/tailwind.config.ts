import { Config } from 'tailwindcss/types/config';

export const tailwindConfig: Config = {
  darkMode: ['class'],
  content: ['./src/**/*.{html,js,jsx,md,mdx,ts,tsx}'],
  presets: [require('./ui.preset.js')],
};
