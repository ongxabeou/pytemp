#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

WORKING_DIR = str(os.environ['DMAI_HOME'])
MODE_WRITE = 'w'
MODE_READ = 'r'
MODE_RUNTIME = 'test'
DMAI_CONFIG_FILE_PATH = WORKING_DIR + '/resources/configs/dmai.conf'
DMAI_LOG_CONFIG_FILE_PATH = WORKING_DIR + '/resources/configs/logging.conf'
DMAI_LOG_FILE_PATH = WORKING_DIR + '/logs/dmai.log'

DMAI_LANG_VI_FILE_PATH = WORKING_DIR + '/resources/lang/message_vi.json'
DMAI_LANG_EN_FILE_PATH = WORKING_DIR + '/resources/lang/message_en.json'


class ADMIN:
    SECTION = 'admin'
    TOKEN = 'token'


class SECTION:
    API_URI = 'api_uri'
    LOGGING_MODE = 'logging_mode'


class LOGGING_MODE:
    WRITE_TRACEBACK_FOR_ALL_CUSTOMIZE_EXCEPTION = 'write_traceback_for_all_customize_exception'
    WRITE_TRACEBACK_FOR_GLOBAL_EXCEPTION = 'write_traceback_for_global_exception'
    LOG_FOR_REQUEST_SUCCESS = 'log_for_request_success'
    LOG_FOR_ALL_CUSTOMIZE_EXCEPTION = 'log_for_all_customize_exception'
    LOG_FOR_GLOBAL_EXCEPTION = 'log_for_global_exception'


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
