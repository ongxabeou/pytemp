#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""

import hashlib

from src.common.lang_config import LANG
from src.common.my_except import InputNotFoundError
from src.libs.caching import LRUCacheDict
from src.libs.singleton import Singleton
from src.models import BOT_STRUCTURE, NLP_APP_STRUCTURE
from src.models.bot_config_repository import BotConfigRepository


@Singleton
class IntentRepository:
    _intent_dic = {}

    def __init__(self):
        nlp_dic = BotConfigRepository().nlp_dic
        for key in nlp_dic.keys():
            self._intent_dic[key] = self.Intent(nlp_dic[key])

    def get(self, bot_id, message):
        """
        lấy intent theo message
        :param bot_id:
        :param message:
        :return:
        """
        try:
            bot = BotConfigRepository().bot_dic[bot_id]
            intent = self._intent_dic[bot[BOT_STRUCTURE.NLP_KEY]]
            intent_str = intent.get(message)
            if intent_str is not None:
                return intent_str
            # nếu không có trong cache thì lấy request lên Wit.ai để lấy intent mới
            # và lưu intent mới vào caching
            return 'getting'
        except KeyError:
            raise InputNotFoundError(LANG.NOT_EXIST, 'bot_id', bot_id)

    class Intent:
        """ lớp tạo caching để lưu trữ các intent """

        def __init__(self, nlp_config):
            """
                :param self:
                :param nlp_config:
            """
            self.nlp_config = nlp_config
            if NLP_APP_STRUCTURE.CACHE_EXPIRED_TIME not in nlp_config:
                self.nlp_config[NLP_APP_STRUCTURE.CACHE_EXPIRED_TIME] = NLP_APP_STRUCTURE.CACHE_EXPIRED_TIME_DEFAULT
            if NLP_APP_STRUCTURE.MAX_CACHE not in nlp_config:
                self.nlp_config[NLP_APP_STRUCTURE.MAX_CACHE] = NLP_APP_STRUCTURE.MAX_CACHE_DEFAULT
            self.my_cache = LRUCacheDict(max_size=self.nlp_config[NLP_APP_STRUCTURE.MAX_CACHE],
                                         expiration=self.nlp_config[NLP_APP_STRUCTURE.CACHE_EXPIRED_TIME])

        def _create_key(self, message):
            """
            tạo key cho caching
            :param self:
            :param message:
            """
            m = hashlib.md5()
            origin_message = '%s%s' % (self.nlp_config[NLP_APP_STRUCTURE.KEY], message)
            m.update(origin_message.encode('utf-8'))
            return m.hexdigest()

        def set(self, intent, message):
            """ lưu message và intent và caching
                :param self:
                :param message:
                :param intent:
            """
            self.my_cache[self._create_key(message)] = intent

        def get(self, message):
            """ lấy intent từ caching
                :param self:
                :param message:
            """
            try:
                return self.my_cache[self._create_key(message)]
            except KeyError:
                return None
