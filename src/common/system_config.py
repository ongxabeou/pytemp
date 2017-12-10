#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import datetime
import logging.config

from bottle import unicode

from common import DMAI_CONFIG_FILE_PATH, DMAI_LOG_CONFIG_FILE_PATH, DMAI_LOG_FILE_PATH
from libs.singleton import Singleton


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
            except Exception as e:
                self.logger.error("get section of SystemConfig %s option %s have error:%s!" % (section, option, e))
                local_dic[option] = None
        self._sections[section] = local_dic
        return local_dic


# --------------------------- TEST ---------------------------
if __name__ == '__main__':

    __sys_conf = SystemConfig()


    def ___cu_chuoi():
        raise KeyError('Cộng hòa')


    def ___man():
        ___cu_chuoi()


    try:
        ___man()
    except KeyError as e:
        __sys_conf.logger.exception('%s :: exception occurred' % str(datetime.datetime.now()))
