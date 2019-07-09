#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""
import configparser
import logging.config
import logging.handlers

from flask.logging import has_level_handler, default_handler

from src.common import PROJECT_CONFIG_FILE_PATH, ERROR_LOG_FILE_PATH, \
    PROJECT_LOG_FILE_PATH, PROJECT_LOG_CONFIG_FILE_PATH
from src.libs.singleton import Singleton


@Singleton
class SystemConfig:
    config = configparser.ConfigParser()
    _sections = {}

    def __init__(self):
        self.config.read(PROJECT_CONFIG_FILE_PATH, 'utf-8')
        # tất cả cấu hình đều lấy từ file logging.conf
        logging.config.fileConfig(PROJECT_LOG_CONFIG_FILE_PATH)
        self.logger = self.get_logger()

    def get_section_map(self, section):
        if section in self._sections:
            return self._sections[section]

        local_dic = {}
        options = self.config.options(section)
        for option in options:
            try:
                local_dic[option] = self.config.get(section, option)
                if local_dic[option] == -1:
                    self.logger.info("skip: %s" % option)
            except Exception as ex:
                self.logger.exception("get section of SystemConfig %s option %s have error:%s!" % (section, option, ex))
                local_dic[option] = None
        self._sections[section] = local_dic
        return local_dic

    def get_logger(self, obj=None):
        if obj:
            if isinstance(obj, str):
                logger = logging.getLogger(obj)
            else:
                logger = logging.getLogger(self._fullname(obj))
        else:
            logger = logging.getLogger()

        for h in logger.handlers:
            # logging.handlers.RotatingFileHandler().level
            try:
                if h.level == logging.ERROR:
                    h.baseFilename = ERROR_LOG_FILE_PATH
                else:
                    h.baseFilename = PROJECT_LOG_FILE_PATH
            except Exception as es:
                print(__name__, es)
                pass

        # if logger.level == logging.NOTSET:
        #     logger.setLevel(logging.DEBUG)
        if not has_level_handler(logger):
            logger.addHandler(default_handler)

        return logger

    @staticmethod
    def _fullname(o):
        # o.__module__ + "." + o.__class__.__qualname__ is an example in
        # this context of H.L. Mencken's "neat, plausible, and wrong."
        # Python makes no guarantees as to whether the __module__ special
        # attribute is defined, so we take a more circumspect approach.
        # Alas, the module name is explicitly excluded from __qualname__
        # in Python 3.

        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__  # Avoid reporting __builtin__
        else:
            return module + '.' + o.__class__.__name__


# --------------------------- TEST ---------------------------
if __name__ == '__main__':

    def ___cu_dump():
        raise KeyError('test log config:: Behavior was simplified. The logger is always named')


    def ___man():
        ___cu_dump()


    try:
        ___man()
    except KeyError as e:
        SystemConfig().logger.warning(e)
        SystemConfig().logger.info(e)
        SystemConfig().logger.debug(e)
        SystemConfig().logger.error(e)
        SystemConfig().logger.exception('exception occurred')


    class TestLog:
        def __init__(self):
            log = SystemConfig().get_logger(self)
            log.warning('test log')
            log.info('test log')
            log.debug('test log')
            log.error('test log')
            log.exception('exception occurred')


    TestLog()
