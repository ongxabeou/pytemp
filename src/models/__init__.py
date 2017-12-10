#!/usr/bin/env python
# -*- coding: utf-8 -*-
from common import WORKING_DIR

CONFIG_BOTS_PATH = WORKING_DIR + '/resources/configs/bots.json'


class BOTS_STRUCTURE:
    BOTS = 'bots'
    NLP_APPS = 'nlp_apps'


class BOT_STRUCTURE:
    ID = 'id'
    NLP_KEY = 'nlp_key'
    NAME = 'name'
    DESC = 'desc'
    TOKEN = 'token'
    CONSUMER = 'consumer'
    META_CLASS = 'meta_class'


class CONSUMER:
    ID = "id"
    NAME = "name"
    PRODUCT = "product"
    PHONE = "phone"
    ADDRESS = "address"
    UNIT = "unit"


class NLP_APP_STRUCTURE:
    KEY = 'key'
    DESC = 'desc'
    CACHE_EXPIRED_TIME = 'cache_expired_time'
    CACHE_EXPIRED_TIME_DEFAULT = 24 * 3600
    MAX_CACHE = 'max_cache'
    MAX_CACHE_DEFAULT = 102400


class PERMITTED_STRUCTURE:
    ADMIN_PERMITTED = 'admin_permitted'
    USER_PERMITTED = 'user_permitted'
    METHODS = 'methods'
