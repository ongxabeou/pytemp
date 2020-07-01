#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os
import sys

from click._unicodefun import click

from src import PROJECT_NAME

os.environ[PROJECT_NAME + "_HOME"], _ = os.path.split(os.path.abspath(__file__))
from src.libs.job import SchedulerFactory
from src.common import SECTION, MONGO_CONFIG
from src.common.system_config import SystemConfig

from src.schedulers.test_scheduler import TestScheduler

from src.models.mongodb_schema import (
    db,
    init_all_data
)


def migrate(teardown):
    if teardown:
        tear_down()
    set_up()


def tear_down():
    db.connection.drop_database(SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.DB])


# supposed to interact with some scripts to generate database
def set_up():
    init_all_data()


def job_process():
    fac = SchedulerFactory()
    fac.set_logger(SystemConfig().logger)
    fac.add(TestScheduler())
    fac.run()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'teardown':
            migrate(True)
        elif mode == 'migrate':
            migrate(False)
        else:
            job_process()
    else:
        job_process()
