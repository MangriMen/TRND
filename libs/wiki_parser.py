import datetime
import math
import time

import requests
from bs4 import BeautifulSoup
from libs import utils


def get_data_from_wiki(worker_, dict_):
    def showError():
        worker_.error.emit(
            str(err.__class__.__name__),
            'Произошла непредвиденная ошибка при загрузке данных.',
            str(err)
        )
    site = 'https://escapefromtarkov.fandom.com'
    urlWeapons = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B8%D0%B5'
    urlMods = 'https://escapefromtarkov.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B5%D0%B9%D0%BD%D1%8B%D0%B5_' \
              '%D1%87%D0%B0%D1%81%D1%82%D0%B8_%D0%B8_%D0%BC%D0%BE%D0%B4%D1%8B '

    weapons = 'weapons'
    mods = 'mods'
    modsConflicts = 'modsConflicts'
    mainBlockClass = 'mw-parser-output'
    weaponNameBlockClass = 'firstHeading'
    modsBlockId = 'Моды'
    modsHeadersClass = 'wds-tabs__wrapper'
    compatibilityTabTitle = 'Совместимость'
    conflictsTabTitle = 'Конфликтующие моды'

    firstLevelFormatStr = '%4s%s'
    secondLevelFormatStr = '%8s%s'
    thirdLevelFormatStr = '%12s%s'

    outDict = utils.validate_data(dict_['jsonData'])

    downloadTime = time.perf_counter()
    if dict_['type'] == weapons or dict_['type'] == mods:
        min_f = 0
        min_s = 0

        if dict_['type'] == weapons:
            maxF = 9  # 9
            maxS = 10e9  # 10e9
            queryPage = urlWeapons
        elif dict_['type'] == mods:
            maxF = 10e9  # 10e9
            maxS = 10e9  # 10e9
            queryPage = urlMods
        else:
            return

        try:
            html = requests.get(queryPage)
            html.raise_for_status()
        except requests.exceptions.RequestException as err:
            showError()
            return

        soup = BeautifulSoup(html.text, 'lxml')
        headers_ = soup.find('div', class_=mainBlockClass).findAll('h3')

        header_counter = 0
        for header_ in headers_:
            if not worker_.isRunning:
                return None

            if header_counter < min_f:
                continue
            elif header_counter >= maxF:
                break
            header_counter += 1

            header = header_.findAll('span')[1].text.strip()
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
                elif inner_counter >= maxS:
                    break
                inner_counter += 1

                td_ = tr_.find('td')
                if td_ is None:
                    continue

                a_ = td_.find('a')
                if a_ is None:
                    continue

                try:
                    r = requests.get(site + a_.get('href'))
                    r.raise_for_status()
                except requests.exceptions.RequestException as err:
                    showError()
                    return

                page = BeautifulSoup(r.text, 'lxml')

                weaponName = page.find('h1', id=weaponNameBlockClass)
                if weaponName is None:
                    continue
                weaponNameStr = weaponName.text.strip()

                modsTitle = page.find('div', class_=mainBlockClass).find('span', id=modsBlockId)
                if modsTitle is None:
                    continue

                if worker_.isRunning:
                    worker_.display_text.emit(firstLevelFormatStr % ('', a_.get('title')))
                worker_.local_progress.emit(int(math.ceil(inner_counter / len(table_) * 100)))

                modsTables = modsTitle.findParent().find_next_sibling().findChild()

                modsTablesHeaders = modsTables.find('div', class_=modsHeadersClass).findAll('a')
                modsTablesData = modsTables.findAll('table')

                for modHeader, modTab in zip(modsTablesHeaders, modsTablesData):
                    if not worker_.isRunning:
                        return None

                    category = modHeader.text.capitalize().strip()
                    if category == compatibilityTabTitle:
                        continue
                    elif category == conflictsTabTitle:
                        outDict[modsConflicts][weaponNameStr] = list()

                    if worker_.isRunning:
                        worker_.display_text.emit(secondLevelFormatStr % ('', category))

                    modTable = modTab.findAll('tr')
                    if modTable is None:
                        continue

                    for modTr in modTable:
                        if not worker_.isRunning:
                            return None

                        if modTr is None:
                            continue

                        modLink = modTr.find('a', class_='')
                        if modLink is None:
                            continue
                        modLinkStr = modLink.text.strip()

                        if worker_.isRunning:
                            worker_.display_text.emit(thirdLevelFormatStr % ('', modLinkStr))

                        if category == conflictsTabTitle:
                            outDict[modsConflicts][weaponNameStr].append(modLinkStr)
                        elif dict_['type'] == weapons:
                            if weaponNameStr not in outDict[dict_['type']]:
                                outDict[dict_['type']][weaponNameStr] = dict()

                            if category not in outDict[dict_['type']][weaponNameStr]:
                                outDict[dict_['type']][weaponNameStr][category] = list()

                            if modLinkStr not in outDict[dict_['type']][weaponNameStr][category]:
                                outDict[dict_['type']][weaponNameStr][category].append(modLinkStr)
                        elif dict_['type'] == mods:
                            if weaponNameStr not in outDict[dict_['type']]:
                                outDict[dict_['type']][weaponNameStr] = list()

                            if modLinkStr not in outDict[dict_['type']][weaponNameStr]:
                                outDict[dict_['type']][weaponNameStr].append(modLinkStr)

    elapsed = time.perf_counter() - downloadTime
    elapsedStr = ("--- %.f minutes %.f seconds ---" % ((elapsed / 60), elapsed % 60))
    worker_.display_text.emit(elapsedStr)

    currentDateIso = datetime.datetime.now().isoformat()
    if dict_['type'] == weapons:
        outDict['weaponsLastUpdate'] = currentDateIso
    elif dict_['type'] == mods:
        outDict['modsLastUpdate'] = currentDateIso

    return outDict
