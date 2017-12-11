#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""

import json

from src.common.lang_config import LANG
from src.common.my_except import LogicSystemError, ParamInvalidError, InputNotFoundError
from src.libs.singleton import Singleton
from src.common import open_file, MODE_WRITE
from src.models import CONFIG_BOTS_PATH, BOT_STRUCTURE, BOTS_STRUCTURE, NLP_APP_STRUCTURE, PERMITTED_STRUCTURE


@Singleton
class BotConfigRepository:
    token_dic = {}
    bot_dic = {}
    nlp_dic = {}
    admin_permitted = {}
    user_permitted = {}
    _bots = {}

    def __init__(self):
        text = open_file(CONFIG_BOTS_PATH).read()
        self._bots = json.loads(text)

        for bot in self._bots[BOTS_STRUCTURE.BOTS]:
            self.bot_dic[bot[BOT_STRUCTURE.ID]] = bot
            self.token_dic[bot[BOT_STRUCTURE.TOKEN]] = bot[BOT_STRUCTURE.ID]
        for nlp in self._bots[BOTS_STRUCTURE.NLP_APPS]:
            self.nlp_dic[nlp[NLP_APP_STRUCTURE.KEY]] = nlp

        self.admin_permitted = self._bots[PERMITTED_STRUCTURE.ADMIN_PERMITTED]
        self.user_permitted = self._bots[PERMITTED_STRUCTURE.USER_PERMITTED]

    def get(self, bot_id):
        if bot_id not in self.bot_dic:
            raise InputNotFoundError(LANG.NOT_EXIST, bot_id.__name__, bot_id)
        return self.bot_dic[bot_id]

    def delete(self, bot_id):
        if bot_id not in self.bot_dic:
            raise InputNotFoundError(LANG.NOT_EXIST, bot_id.__name__, bot_id)
        self._bots[BOTS_STRUCTURE.BOTS].remove(self.bot_dic[bot_id])
        self.bot_dic[bot_id] = None
        str_json = json.dumps(self._bots, ensure_ascii=False)
        open_file(CONFIG_BOTS_PATH, MODE_WRITE).write(str_json)

    def set(self, bot_id, bot_config):
        if bot_id not in self.bot_dic:
            raise InputNotFoundError(LANG.NOT_EXIST, bot_id.__name__, bot_id)

        index = self._bots[BOTS_STRUCTURE.BOTS].index(self.bot_dic[bot_id])
        self.bot_dic[bot_id] = bot_config
        self._bots[BOTS_STRUCTURE.BOTS][index] = bot_config
        str_json = json.dumps(self._bots, ensure_ascii=False)
        open_file(CONFIG_BOTS_PATH, MODE_WRITE).write(str_json)

    def register(self, bot_id, bot_config):
        if bot_id in self.bot_dic:
            raise LogicSystemError(LANG.ALREADY_EXIST, bot_id.__name__, bot_id)

        self.bot_dic[bot_id] = bot_config
        self._bots[BOTS_STRUCTURE.BOTS].append(bot_config)

        str_json = json.dumps(self._bots, ensure_ascii=False)
        open_file(CONFIG_BOTS_PATH, MODE_WRITE).write(str_json)

    def get_nlp_app(self, nlp_key):
        if nlp_key is None:
            raise ParamInvalidError(LANG.MUST_NOT_EMPTY, nlp_key.__name__)
        try:
            return self.nlp_dic[nlp_key]
        except KeyError:
            raise InputNotFoundError(LANG.NOT_EXIST, nlp_key.__name__, nlp_key)
