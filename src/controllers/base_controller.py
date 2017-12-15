#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""

from flask import request

from src.common.lang_config import LANG_VI, LANG_EN, LANG
from src.common.my_except import ParamInvalidError
from src.libs.http_validator import VALIDATION_RESULT, HttpValidator


class BaseController(object):

    @staticmethod
    def abort_if_invalid(rules, data):
        valid = HttpValidator(rules)
        val_result = valid.validate_object(data)
        if not val_result[VALIDATION_RESULT.VALID]:
            errors = val_result[VALIDATION_RESULT.ERRORS]
            raise ParamInvalidError(LANG.VALIDATE_ERROR, errors)

    @staticmethod
    def abort_if_param_none_or_empty(param, param_name):
        if param is None or param is '':
            raise ParamInvalidError(LANG.MUST_NOT_EMPTY, param_name)

    def __init__(self):
        param = request.args.get('lang')
        if param and param not in (LANG_VI, LANG_EN):
            raise ParamInvalidError(LANG.LANG_ERROR)
