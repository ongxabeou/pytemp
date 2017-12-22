#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""
import datetime
import hashlib
from functools import wraps

from flask import request

from src.common import SECTION, LOGGING_MODE, get_request_id
from src.common.lang_config import LangConfig, LANG, LANG_STRUCTURE, LANG_VI, LANG_EN
from src.common.system_config import SystemConfig
from src.libs.thread_pool import ThreadPool


class BaseMoError(Exception):
    """ Attribute not found. """

    def __init__(self, *args):  # real signature unknown
        # *args is used to get a list of the parameters passed in
        param = None
        array = [a for a in args]
        try:
            param = request.args.get('lang')
            if len(array) > 0:
                array[0].encode('utf-8')
            self.params = array
        except:
            self.params = array[1:]

        if (param is None) or (param and param not in (LANG_VI, LANG_EN)):
            param = LANG_VI
        self.lang = LangConfig().lang_map(param)
        self.message_name_default = LANG.VALIDATE_ERROR

        self.sys_conf = SystemConfig()

    def get_message(self):
        try:
            return self._get_message()
        except:
            self.sys_conf.logger.exception('%s :: %s exception occurred' %
                                           (str(datetime.datetime.now()), self.get_class_name()))
            code = self.lang[LANG.INTERNAL_SERVER_ERROR][LANG_STRUCTURE.CODE]
            message = self.lang[LANG.INTERNAL_SERVER_ERROR][LANG_STRUCTURE.MESSAGE]
            return BaseMoError.build_message_error(code, message)

    def _get_message(self):
        log_mod = self.sys_conf.get_section_map(SECTION.LOGGING_MODE)

        len_arg = len(self.params)
        message_name = self.message_name_default
        if len_arg > 0:
            message_name = self.params[0]

        log_message = None
        if message_name not in self.lang:
            log_message = "arg[0] là [%s] không được định nghĩa trong file Lang" % message_name
            message_name = self.message_name_default

        code = self.lang[message_name][LANG_STRUCTURE.CODE]
        message = self.lang[message_name][LANG_STRUCTURE.MESSAGE]

        is_custom_except = message_name != LANG.INTERNAL_SERVER_ERROR and message_name != LANG.MESSAGE_SUCCESS
        mod1 = int(log_mod[LOGGING_MODE.LOG_FOR_ALL_CUSTOMIZE_EXCEPTION]) == 1 and is_custom_except
        mod2 = int(log_mod[LOGGING_MODE.WRITE_TRACEBACK_FOR_ALL_CUSTOMIZE_EXCEPTION]) == 1 and is_custom_except

        mod3 = int(log_mod[LOGGING_MODE.WRITE_TRACEBACK_FOR_GLOBAL_EXCEPTION]) == 1
        mod3 = mod3 and message_name == LANG.INTERNAL_SERVER_ERROR
        mod4 = int(log_mod[LOGGING_MODE.LOG_FOR_GLOBAL_EXCEPTION]) == 1
        mod4 = mod4 and message_name == LANG.INTERNAL_SERVER_ERROR

        mod5 = int(log_mod[LOGGING_MODE.LOG_FOR_REQUEST_SUCCESS]) == 1
        mod5 = mod5 and message_name == LANG.MESSAGE_SUCCESS

        if mod1 or mod2 or mod3 or mod4 or mod5:
            self.sys_conf.logger.debug('==================================================================')
            if log_message:
                self.sys_conf.logger.debug(log_message)

        errors = None
        if len_arg > 1:
            errors = self.params[1]

        try:
            if mod1 or mod4 or mod5:
                self.sys_conf.logger.debug(
                    'request_id: {request_id} \n HTTP/1.1 {method} {url}\n{headers}\n\nbody: {body}'.format(
                        request_id=get_request_id(),
                        method=request.method,
                        url=request.url,
                        headers='\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
                        body=request.data
                    ))
        except:
            pass

        if mod2 or mod3:
            self.sys_conf.logger.exception('%s :: %s exception occurred' %
                                           (str(datetime.datetime.now()), self.get_class_name()))

        if message and str(message).find('%s') >= 0:
            params = list(self.params[1:])
            message = message % tuple(params)
            return BaseMoError.build_message_error(code, message)
        else:
            return BaseMoError.build_message_error(code, message, errors)

    @staticmethod
    def build_message_error(code, message, errors=None):
        if errors:
            return {
                LANG_STRUCTURE.CODE: code,
                LANG_STRUCTURE.MESSAGE: message,
                'errors': errors
            }
        return {
            LANG_STRUCTURE.CODE: code,
            LANG_STRUCTURE.MESSAGE: message
        }

    def get_class_name(self):
        return self.__class__.__name__


class ParamInvalidError(BaseMoError):
    def __init__(self, *args):  # real signature unknown
        super(ParamInvalidError, self).__init__(self, *args)
        self.message_name_default = LANG.VALIDATE_ERROR


class InputNotFoundError(BaseMoError):
    def __init__(self, *args):  # real signature unknown
        super(InputNotFoundError, self).__init__(self, *args)
        self.message_name_default = LANG.NOT_FOUND


class LogicSystemError(BaseMoError):
    def __init__(self, *args):  # real signature unknown
        super(LogicSystemError, self).__init__(self, *args)
        self.message_name_default = LANG.NOT_ALLOWED


# --------------------------- TEST ---------------------------
if __name__ == '__main__':

    def _try_catch_error2(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                print('ok 2')
                return f(*args, **kwargs)
            except BaseMoError as e:
                print('error 2 %s' % e)

        return decorated


    def _try_catch_error1(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                print('ok 1')
                return f(*args, **kwargs)
            except BaseMoError as e:
                print('error 1 %s' % e.get_message())

        return decorated


    @_try_catch_error2
    @_try_catch_error1
    def __function():
        raise BaseMoError('text')


    try:
        __function()
    except Exception as e:
        print(e.args)
