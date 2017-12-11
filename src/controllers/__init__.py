#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.common import WORKING_DIR

BOT_SINGLE_SELLER_SCRIPT_PATH = WORKING_DIR + '/resources/scripts/bot_single_seller.script.json'


class CUSTOMER_STRUCTURE:
    ID = 'id'
    NAME = 'name'
    GENDER = 'gender'
    AGE = 'age'
    MESSAGE = 'message'


class META_CLASS:
    MODULE_NAME = 'module_name'
    CLASS_NAME = 'class_name'
