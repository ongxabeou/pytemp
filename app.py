#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os

from click._unicodefun import click
from flask.cli import FlaskGroup

from src import PROJECT_NAME, PROJECT_QUEUE

os.environ[PROJECT_NAME + "_HOME"], _ = os.path.split(os.path.abspath(__file__))

from src.schedulers.customer_queue_process import customer_process_callback
from src.common import SECTION, MONGO_CONFIG
from src.common.system_config import SystemConfig
from src.libs.job import SchedulerFactory
from src.schedulers.test_scheduler import TestScheduler

from flask import Flask
from flask_cors import CORS
from src.apis.bot import bot_mod
from src.models.mongodb_schema import (
    db,
    init_all_data
)
from src.libs.simple_queue import SimpleQueueFactory


def add_api_route(app, api_mod):
    SystemConfig().logger.info('register api route for %s' % api_mod.name)
    app.register_blueprint(api_mod)


def create_app():
    app = Flask(__name__)

    # khởi tạo các queue cho project
    SimpleQueueFactory().add(queue_name=PROJECT_QUEUE.CUSTOMER_QUEUE,
                             call_back_function=customer_process_callback)

    # load config for MongoDB
    app.config[SECTION.MONGODB_SETTINGS] = {
        MONGO_CONFIG.ALIAS: SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.ALIAS],
        MONGO_CONFIG.HOST: SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.HOST],
        MONGO_CONFIG.PORT: int(SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.PORT]),
        MONGO_CONFIG.DB: SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.DB],
    }

    SystemConfig().logger.info('==================================================================')
    add_api_route(app, bot_mod)

    db.init_app(app)

    CORS(app)

    return app


cli = FlaskGroup(create_app=create_app)


@cli.command()
@click.option("--teardown")
def migrate(teardown):
    if teardown:
        tear_down()
    set_up()


def tear_down():
    db.connection.drop_database(SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.DB])


# supposed to interact with some scripts to generate database
def set_up():
    init_all_data()


@cli.command()
def job_process():
    fac = SchedulerFactory()
    fac.set_logger(SystemConfig().logger)
    fac.add(TestScheduler())
    fac.run()


if __name__ == "__main__":
    cli()
