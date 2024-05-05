import datetime
import inspect
import json
import logging
import os
import re
import sys
import tempfile
import threading
from pathlib import Path

import requests

from libs import consts


def load_data(filePath=None):
    if filePath is None:
        filePath = os.environ.get('DATA_FILE_PATH')
    try:
        with open(filePath, 'r', encoding='utf-8') as fileIn:
            try:
                json_ = json.load(fileIn)
            except json.decoder.JSONDecodeError:
                json_ = None
    except FileNotFoundError:
        return None
    else:
        return json_


def dump_data(dict_, filePath=None):
    if filePath is None:
        filePath = os.environ.get('DATA_FILE_PATH')
    try:
        with open(filePath, 'w', encoding='utf-8') as fileOut:
            json.dump(dict_, fileOut, indent=2, ensure_ascii=False)
    except (FileNotFoundError, PermissionError) as err:
        raise err


def get_json_dumps(dict_):
    return json.dumps(dict_, indent=2, ensure_ascii=False) if isinstance(dict_, dict) else None


def get_json_loads(str_):
    try:
        json_ = json.loads(str_)
    except json.decoder.JSONDecodeError:
        return None
    else:
        return json_


def rewrite_file_to_file(fileInPath, fileOutPath):
    try:
        with open(fileInPath, 'r', encoding='utf-8') as fileIn:
            with open(fileOutPath, "w", encoding='utf-8') as fileOut:
                for line in fileIn:
                    fileOut.write(line)
    except FileNotFoundError:
        return False
    else:
        return True


def date_to_str(isoDate, format_str):
    if isoDate == 'unknown':
        return 'неизвестно'

    try:
        out = datetime.datetime.fromisoformat(isoDate).strftime(format_str)
    except ValueError:
        isoDate = datetime.datetime.now().isoformat()
        out = date_to_str(isoDate, format_str)

    return out


def thread_print(caller):
    print('%-25s: %s, %s,' % (caller, threading.current_thread().name, threading.current_thread().ident))


def get_update_info(githubLinkLatestRelease):
    try:
        response = requests.get(githubLinkLatestRelease)
        response.raise_for_status()
        response = response.json()
    except requests.exceptions.RequestException as err:
        return {'result': False, 'error': str(err.__class__.__name__), 'error_msg': str(err), 'data': err.response}
    except json.JSONDecodeError as err:
        return {'result': False, 'error': str(err.__class__.__name__), 'error_msg': str(err), 'data': None}

    result = True
    error = None
    error_msg = None

    if 'message' in response:
        if re.search('rate limit', response['message']):
            result = False
            error = 'Rate Limit'
            error_msg = 'Превышено количество запросов. Попробуйте позже.'
        elif response['message'] == 'Not Found':
            result = False
            error = 'Not Found'
            error_msg = 'Не найден список версий.'

    return {'result': result, 'error': error, 'error_msg': error_msg, 'data': response}


def validate_data(jsonData):
    if jsonData is None:
        jsonData = dict()
    if consts.DATA_WEAPONS_LAST_UPDATE_KEY not in jsonData:
        jsonData[consts.DATA_WEAPONS_LAST_UPDATE_KEY] = 'unknown'
    if consts.DATA_MODS_LAST_UPDATE_KEY not in jsonData:
        jsonData[consts.DATA_MODS_LAST_UPDATE_KEY] = 'unknown'
    if consts.DATA_WEAPONS_KEY not in jsonData:
        jsonData[consts.DATA_WEAPONS_KEY] = dict()
    if consts.DATA_MODS_KEY not in jsonData:
        jsonData[consts.DATA_MODS_KEY] = dict()
    if consts.DATA_MODS_CONFLICTS_KEY not in jsonData:
        jsonData[consts.DATA_MODS_CONFLICTS_KEY] = dict()

    return jsonData


def clear_dir(directoryPath):
    directory = Path(directoryPath)
    for item in directory.iterdir():
        if item.is_dir():
            clear_dir(item)
        else:
            item.unlink()


def create_logger(name, level=logging.INFO,
                  *, dateFormat='%Y-%m-%d_%H-%M-%S', folderPath=None, loggerFormat=None, maxCount=50, extension='.log'):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    folderPath = os.path.abspath(folderPath if folderPath is not None else os.path.join(tempfile.tempdir, __name__))
    fileName = ''.join([datetime.datetime.now().strftime(dateFormat), extension])
    filePath = os.path.join(folderPath, fileName)

    formatter = logging.Formatter(loggerFormat) if loggerFormat is not None else None

    handlers = dict()
    error = ''

    try:
        if len((fileList := os.listdir(folderPath))) > maxCount:
            os.remove(os.path.join(folderPath, fileList[0]))

        handlers['fileHandler'] = logging.FileHandler(filePath)
    except WindowsError as error:
        handlers['fileHandler'] = None
        handlers['streamHandler'] = logging.StreamHandler(sys.stdout)

    for handlerName, handler in handlers.items():
        if handler is not None:
            if formatter is not None:
                handler.setFormatter(formatter)
            logger.addHandler(handler)

    if error:
        logger.error(error)

    logger.info(''.join(['Logger initialized to ', 'stdout' if handlers['fileHandler'] is None else 'file handler']))


def get_logger_for_module():
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    return logging.getLogger(''.join([consts.PROGRAM_NAME, '.', mod.__name__]))
