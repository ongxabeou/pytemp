#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""
import configparser
import datetime
import logging.config

from src.common import DMAI_CONFIG_FILE_PATH, DMAI_LOG_CONFIG_FILE_PATH, DMAI_LOG_FILE_PATH
from src.libs.singleton import Singleton


@Singleton
class SystemConfig:
    config = configparser.ConfigParser()
    _sections = {}

    def __init__(self):
        self.config.read(DMAI_CONFIG_FILE_PATH, 'utf-8')
        logging.config.fileConfig(DMAI_LOG_CONFIG_FILE_PATH, None, disable_existing_loggers=False)
        self.logger = logging.getLogger('common.system_config.SystemConfig')
        self.logger.addHandler(logging.FileHandler(DMAI_LOG_FILE_PATH, encoding='utf-8'))

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


# --------------------------- TEST ---------------------------
if __name__ == '__main__':

    __sys_conf = SystemConfig()


    def ___cu_dump():
        raise KeyError('Cộng hòa')


    def ___man():
        ___cu_dump()


    try:
        ___man()
    except KeyError as e:
        __sys_conf.logger.exception('%s :: exception occurred' % str(datetime.datetime.now()))
