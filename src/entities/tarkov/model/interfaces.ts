export interface TarkovDownloadProgress {
  current_size: number;
  full_size: number;
}

export interface Weapon {
  name: string;
  icon_link: string;
  wiki_link: string;
  slots: Slot[];
}

export interface Slot {
  id: string;
  name: string;
  icon_link: string;
  wiki_link: string;
}
