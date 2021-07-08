import datetime
import json
import platform
from math import ceil
import os
import time
import requests
from bs4 import BeautifulSoup


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def creation_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat_ = os.stat(path_to_file)
        try:
            return stat_.st_birthtime
        except AttributeError:
            return stat_.st_mtime


def get_data_from_site(main):
    site = 'https://escapefromtarkov.fandom.com'
    url_weapons = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B8%D0%B5'
    url_mods = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B5%D0%B9%D0%BD%D1%8B%D0%B5_' \
               '%D1%87%D0%B0%D1%81%D1%82%D0%B8_%D0%B8_%D0%BC%D0%BE%D0%B4%D1%8B '

    min_s = 0
    max_s = 10e9  # 10e9

    if main.JsonData is None:
        wp_dict = dict()
    else:
        wp_dict = main.JsonData
    if 'weaponsLastUpdate' not in wp_dict:
        wp_dict['weaponsLastUpdate'] = 'unknown'
    if 'modsLastUpdate' not in wp_dict:
        wp_dict['modsLastUpdate'] = 'unknown'
    if 'weapons' not in wp_dict:
        wp_dict['weapons'] = dict()
    if 'mods' not in wp_dict:
        wp_dict['mods'] = dict()

    download_time = time.perf_counter()

    if main.type == 'weapons':
        min_f = 0
        max_f = 9  # 9

        html = requests.get(url_weapons)
        soup = BeautifulSoup(html.text, 'lxml')

        parser_output = soup.find('div', class_='mw-parser-output')
        headers_ = parser_output.findAll('h3')

        header_counter = 0
        for header_ in headers_:
            if header_counter < min_f:
                continue
            elif header_counter >= max_f:
                break
            header_counter += 1

            header = header_.findAll('span')[1].text
            main.display_text.emit(header)
            main.global_progress.emit(int(ceil(header_counter / len(headers_) * 100)))

            table_ = header_.find_next_sibling().tbody.findAll('tr')

            inner_counter = 0
            for tr_ in table_:
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

                main.display_text.emit('%4s%s' % ('', a_.get('title')))
                main.local_progress.emit(int(ceil(inner_counter / len(table_) * 100)))

                if mods is None:
                    continue

                mods_tables = mods.findParent().find_next_sibling().findChild().findAll('div')

                for mod_tab in mods_tables:
                    category = mod_tab.get('title').capitalize()
                    main.display_text.emit('%8s%s' % ('', category))

                    mod_table = mod_tab.findAll('tr')
                    if mod_table is None:
                        continue

                    for mod_tr in mod_table:
                        if mod_tr is None:
                            continue

                        mod_a = mod_tr.find('a', class_='')
                        if mod_a is None:
                            continue

                        main.display_text.emit('%12s%s' % ('', mod_a.text))

                        if weapon_name.text not in wp_dict[main.type]:
                            wp_dict[main.type][weapon_name.text] = dict()

                        if category not in wp_dict[main.type][weapon_name.text]:
                            wp_dict[main.type][weapon_name.text][category] = list()

                        if mod_a.text not in wp_dict[main.type][weapon_name.text][category]:
                            wp_dict[main.type][weapon_name.text][category].append(mod_a.text)

                        if not main.isRunning:
                            return None
    elif main.type == 'mods':
        min_f = 0
        max_f = 10e9  # 10e9

        html = requests.get(url_mods)
        soup = BeautifulSoup(html.text, 'lxml')

        parser_output = soup.find('div', class_='mw-parser-output')
        headers_ = parser_output.findAll('h3')

        header_counter = 0
        for header_ in headers_:
            if header_counter < min_f:
                continue
            elif header_counter >= max_f:
                break
            header_counter += 1

            header = header_.findAll('span')[1].text
            main.display_text.emit(header)
            main.global_progress.emit(int(ceil(header_counter / len(headers_) * 100)))

            table_ = header_.find_next_sibling()
            if table_.name == 'h4':
                table_ = header_.find_next_sibling().find_next_sibling().tbody.findAll('tr')
            else:
                table_ = table_.tbody.findAll('tr')

            inner_counter = 0
            for tr_ in table_:
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

                main.display_text.emit('%4s%s' % ('', a_.get('title')))
                main.local_progress.emit(int(ceil(inner_counter / len(table_) * 100)))

                if mods is None:
                    continue

                mods_tables = mods.findParent().find_next_sibling().findChild().findAll('div')

                for mod_tab in mods_tables:
                    category = mod_tab.get('title').capitalize()
                    if category == 'Совместимость':
                        continue
                    main.display_text.emit('%8s%s' % ('', category))

                    mod_table = mod_tab.findAll('tr')
                    if mod_table is None:
                        continue

                    for mod_tr in mod_table:
                        if mod_tr is None:
                            continue

                        mod_a = mod_tr.find('a', class_='')
                        if mod_a is None:
                            continue

                        main.display_text.emit('%12s%s' % ('', mod_a.text))

                        if weapon_name.text not in wp_dict[main.type]:
                            wp_dict[main.type][weapon_name.text] = list()

                        # if category not in wp_dict[main.type][weapon_name.text]:
                        #     wp_dict[main.type][weapon_name.text][category] = set()

                        if mod_a.text not in wp_dict[main.type][weapon_name.text]:
                            wp_dict[main.type][weapon_name.text].append(mod_a.text)

                        if not main.isRunning:
                            return None

    elapsed = time.perf_counter() - download_time
    elapsed_str = ("--- %.f minutes %.f seconds ---" % ((elapsed / 60), elapsed % 60))

    if main.is_debug:
        print(elapsed_str)

    main.display_text.emit(elapsed_str)

    now_date = datetime.datetime.now().isoformat()
    if main.type == 'weapons':
        wp_dict['weaponsLastUpdate'] = now_date
    elif main.type == 'mods':
        wp_dict['modsLastUpdate'] = now_date

    print("WP" + wp_dict['weaponsLastUpdate'].__str__())
    print("MD" + wp_dict['modsLastUpdate'].__str__())

    return wp_dict


def write_data_to_file(wp_dict):
    with open(os.environ.get('DATAFILE'), 'w', encoding='utf-8') as fileOut:
        json.dump(wp_dict, fileOut, indent=2, default=serialize_sets, ensure_ascii=False)


def get_data_from_file():
    try:
        last_change_time = creation_date(os.environ.get('DATAFILE'))
        with open(os.environ.get('DATAFILE'), 'r', encoding='utf-8') as fileIn:
            try:
                json_ = json.load(fileIn)
            except json.decoder.JSONDecodeError:
                json_ = None
    except FileNotFoundError:
        return None, "File not found"
    else:
        return json_, last_change_time
