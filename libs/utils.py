import datetime
import json
import os
import re
import threading

import requests


def load_data():
    try:
        with open(os.environ.get('DATAFILE'), 'r', encoding='utf-8') as fileIn:
            try:
                json_ = json.load(fileIn)
            except json.decoder.JSONDecodeError:
                json_ = None
    except FileNotFoundError:
        return None
    else:
        return json_


def dump_data(out_dict):
    with open(os.environ.get('DATAFILE'), 'w', encoding='utf-8') as fileOut:
        json.dump(out_dict, fileOut, indent=2, ensure_ascii=False)


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


def date_to_str(iso_date, format_str):
    if iso_date == 'unknown':
        return 'неизвестно'

    out = ''
    try:
        out = datetime.datetime.fromisoformat(iso_date).strftime(format_str)
    except ValueError:
        iso_date = datetime.datetime.now().isoformat()
        out = date_to_str(iso_date, format_str)
    finally:
        return out


def thread_print(caller):
    print('%-25s: %s, %s,' % (caller, threading.current_thread().name, threading.current_thread().ident))


def get_update_info(githubLinkLatestRelease):
    try:
        response = requests.get(githubLinkLatestRelease)
        response.raise_for_status()
        response = response.json()
    except requests.exceptions.HTTPError as err:
        return {'result': False, 'error': "HTTP Error", 'error_msg': str(err), 'data': err.response}
    except requests.exceptions.ConnectionError as err:
        return {'result': False, 'error': "Connection Error", 'error_msg': str(err), 'data': err.response}
    except requests.exceptions.Timeout as err:
        return {'result': False, 'error': "Timeout Error", 'error_msg': str(err), 'data': err.response}
    except requests.exceptions.RequestException as err:
        return {'result': False, 'error': "Other Error", 'error_msg': str(err), 'data': err.response}
    except json.JSONDecodeError as err:
        return {'result': False, 'error': "JSON Decode Error", 'error_msg': str(err), 'data': None}

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
