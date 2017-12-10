#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""

from flask import request

from common.lang_config import LANG_VI, LANG_EN, LANG
from common.my_except import ParamInvalidError
from libs.http_validator import VALIDATION_RESULT, HttpValidator


class BaseController(object):
    PARAM_INVALID_VALUE = 412

    @staticmethod
    def abort_if_validate_error(rules, data):
        valid = HttpValidator(rules)
        val_result = valid.validate_object(data)
        if not val_result[VALIDATION_RESULT.VALID]:
            errors = val_result[VALIDATION_RESULT.ERRORS]
            raise ParamInvalidError(LANG.VALIDATE_ERROR, errors)

    @staticmethod
    def abort_if_param_empty_error(param, param_name):
        if param is None or param is '':
            raise ParamInvalidError(LANG.MUST_NOT_EMPTY, param_name)

    def __init__(self):
        param = request.args.get('lang')
        if param and param not in (LANG_VI, LANG_EN):
            raise ParamInvalidError(LANG.LANG_ERROR)
