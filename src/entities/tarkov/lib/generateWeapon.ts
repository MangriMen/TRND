import { invoke } from '@tauri-apps/api';

import { Weapon } from '../model';

export const generateWeapon = () => invoke<Weapon>('generate_weapon');
