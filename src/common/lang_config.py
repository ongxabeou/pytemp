""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""
import json

from src.common import DMAI_LANG_VI_FILE_PATH, DMAI_LANG_EN_FILE_PATH, open_file
from src.libs.singleton import Singleton


def _lang_json(lang='vi'):
    path = DMAI_LANG_VI_FILE_PATH
    if lang == 'en':
        path = DMAI_LANG_EN_FILE_PATH

    with open_file(path) as data_file:
        data = json.loads(data_file.read())

    return data


LANG_VI = 'vi'
LANG_EN = 'en'


class LANG:
    UNAUTHORIZED = 'unauthorized'
    NOT_ALLOWED = 'not_allowed'
    NOT_FOUND = 'not_found'
    INTERNAL_SERVER_ERROR = 'internal_server_error'
    VALIDATE_ERROR = 'validate_error'
    LANG_ERROR = 'lang_error'
    MUST_NOT_EMPTY = 'must_not_empty'
    NOT_EXIST = 'not_exist'
    ALREADY_EXIST = 'already_exist'
    MESSAGE_SUCCESS = 'message_success'


class LANG_STRUCTURE:
    MESSAGE = 'message'
    CODE = 'code'


@Singleton
class LangConfig:
    def __init__(self):
        self.config_lang_vi = _lang_json(LANG_VI)
        self.config_lang_en = _lang_json(LANG_EN)

    def lang_map(self, lang='vi'):
        config_lang_dic = self.config_lang_vi
        if lang == 'en':
            config_lang_dic = self.config_lang_en
        return config_lang_dic
