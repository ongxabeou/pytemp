#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import hashlib
import os

from flask import request

WORKING_DIR = str(os.environ['DMAI_HOME'])
MODE_WRITE = 'w'
MODE_READ = 'r'
MODE_RUNTIME = 'test'
PYTEMP_CONFIG_FILE_PATH = WORKING_DIR + '/resources/configs/pytemp.conf'
PYTEMP_LOG_CONFIG_FILE_PATH = WORKING_DIR + '/resources/configs/logging.conf'
PYTEMP_LOG_FILE_PATH = WORKING_DIR + '/logs/pytemp.log'

PYTEMP_LANG_VI_FILE_PATH = WORKING_DIR + '/resources/lang/message_vi.json'
PYTEMP_LANG_EN_FILE_PATH = WORKING_DIR + '/resources/lang/message_en.json'
COLLECTION_PATH = WORKING_DIR + '/resources/scripts/'

class ADMIN:
    SECTION = 'admin'
    TOKEN = 'token'


class SECTION:
    API_URI = 'api_uri'
    LOGGING_MODE = 'logging_mode'
    MONGODB_SETTINGS = 'MONGODB_SETTINGS'


class LOGGING_MODE:
    WRITE_TRACEBACK_FOR_ALL_CUSTOMIZE_EXCEPTION = 'write_traceback_for_all_customize_exception'
    WRITE_TRACEBACK_FOR_GLOBAL_EXCEPTION = 'write_traceback_for_global_exception'
    LOG_FOR_REQUEST_SUCCESS = 'log_for_request_success'
    LOG_FOR_ALL_CUSTOMIZE_EXCEPTION = 'log_for_all_customize_exception'
    LOG_FOR_GLOBAL_EXCEPTION = 'log_for_global_exception'
    FILE_MAX_BYTES = 'file_max_bytes'
    FILE_BACKUP_COUNT = 'file_backup_count'


class MONGO_CONFIG:
    DB = 'db'
    HOST = 'host'
    PORT = 'port'
    ALIAS = 'alias'


def open_file(file_path, mode=MODE_READ):
    """
    mở file txt
    :param mode:
    :param file_path:
    :return:
    """
    try:
        return open(file_path, encoding='UTF-8', mode=mode)
    except UnicodeDecodeError:
        return open(file_path, encoding='ASCII', mode=mode)


def get_request_id():
    identify = ("{url} {time} ".format(url=request.url, time=str(datetime.datetime.now()))).encode('utf-8')
    return hashlib.md5(identify).hexdigest()
