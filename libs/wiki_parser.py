import datetime
import math
import time

import requests
from bs4 import BeautifulSoup


def get_data_from_wiki(worker_, dict_):
    site = 'https://escapefromtarkov.fandom.com'
    url_weapons = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B8%D0%B5'
    url_mods = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B5%D0%B9%D0%BD%D1%8B%D0%B5_' \
               '%D1%87%D0%B0%D1%81%D1%82%D0%B8_%D0%B8_%D0%BC%D0%BE%D0%B4%D1%8B '

    min_s = 0
    max_s = 10e9  # 10e9

    if dict_['jsonData'] is None:
        out_dict = dict()
    else:
        out_dict = dict_['jsonData']
    if 'weaponsLastUpdate' not in out_dict:
        out_dict['weaponsLastUpdate'] = 'unknown'
    if 'modsLastUpdate' not in out_dict:
        out_dict['modsLastUpdate'] = 'unknown'
    if 'weapons' not in out_dict:
        out_dict['weapons'] = dict()
    if 'mods' not in out_dict:
        out_dict['mods'] = dict()

    download_time = time.perf_counter()

    if dict_['type'] == 'weapons' or dict_['type'] == 'mods':
        min_f = 0

        if dict_['type'] == 'weapons':
            max_f = 9  # 9
            html = requests.get(url_weapons)
        elif dict_['type'] == 'mods':
            max_f = 10e9
            html = requests.get(url_mods)
        else:
            return

        soup = BeautifulSoup(html.text, 'lxml')

        parser_output = soup.find('div', class_='mw-parser-output')
        headers_ = parser_output.findAll('h3')

        header_counter = 0
        for header_ in headers_:
            if not worker_.isRunning:
                return None

            if header_counter < min_f:
                continue
            elif header_counter >= max_f:
                break
            header_counter += 1

            header = header_.findAll('span')[1].text
            if worker_.isRunning:
                worker_.display_text.emit(header)
            worker_.global_progress.emit(int(math.ceil(header_counter / len(headers_) * 100)))

            table_ = header_.find_next_sibling()
            if table_.name == 'h4':
                table_ = header_.find_next_sibling().find_next_sibling().tbody.findAll('tr')
            else:
                table_ = table_.tbody.findAll('tr')

            inner_counter = 0
            for tr_ in table_:
                if not worker_.isRunning:
                    return None

                if inner_counter < min_s:
                    continue
                elif inner_counter >= max_s:
                    break
                inner_counter += 1

                td_ = tr_.find('td')
                if td_ is None:
                    continue

                a_ = td_.find('a')
                if a_ is None:
                    continue

                r = requests.get(site + a_.get('href'))
                page = BeautifulSoup(r.text, 'lxml')

                weapon_name = page.find('h1', class_='firstHeading')
                mods = page.find('div', class_='mw-parser-output').find('span', id='Моды')

                if worker_.isRunning:
                    worker_.display_text.emit('%4s%s' % ('', a_.get('title')))
                worker_.local_progress.emit(int(math.ceil(inner_counter / len(table_) * 100)))

                if mods is None:
                    continue

                mods_tables = mods.findParent().find_next_sibling().findChild().findAll('div')

                for mod_tab in mods_tables:
                    if not worker_.isRunning:
                        return None

                    category = mod_tab.get('title').capitalize()
                    if category == 'Совместимость':
                        continue

                    if worker_.isRunning:
                        worker_.display_text.emit('%8s%s' % ('', category))

                    mod_table = mod_tab.findAll('tr')
                    if mod_table is None:
                        continue

                    for mod_tr in mod_table:
                        if not worker_.isRunning:
                            return None

                        if mod_tr is None:
                            continue

                        mod_a = mod_tr.find('a', class_='')
                        if mod_a is None:
                            continue

                        if worker_.isRunning:
                            worker_.display_text.emit('%12s%s' % ('', mod_a.text))

                        if dict_['type'] == 'weapons':
                            if weapon_name.text not in out_dict[dict_['type']]:
                                out_dict[dict_['type']][weapon_name.text] = dict()

                            if category not in out_dict[dict_['type']][weapon_name.text]:
                                out_dict[dict_['type']][weapon_name.text][category] = list()

                            if mod_a.text not in out_dict[dict_['type']][weapon_name.text][category]:
                                out_dict[dict_['type']][weapon_name.text][category].append(mod_a.text)
                        elif dict_['type'] == 'mods':
                            if weapon_name.text not in out_dict[dict_['type']]:
                                out_dict[dict_['type']][weapon_name.text] = list()

                            if mod_a.text not in out_dict[dict_['type']][weapon_name.text]:
                                out_dict[dict_['type']][weapon_name.text].append(mod_a.text)

    elapsed = time.perf_counter() - download_time
    elapsed_str = ("--- %.f minutes %.f seconds ---" % ((elapsed / 60), elapsed % 60))

    if dict_['is_debug']:
        print(elapsed_str)

    worker_.display_text.emit(elapsed_str)

    now_date = datetime.datetime.now().isoformat()
    if dict_['type'] == 'weapons':
        out_dict['weaponsLastUpdate'] = now_date
    elif dict_['type'] == 'mods':
        out_dict['modsLastUpdate'] = now_date

    return out_dict
