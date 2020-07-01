#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os

from src import PROJECT_QUEUE, PROJECT_NAME

os.environ[PROJECT_NAME + "_HOME"], _ = os.path.split(os.path.abspath(__file__))

from src.schedulers.customer_queue_process import customer_process_callback
from src.common import SECTION, MONGO_CONFIG
from src.common.system_config import SystemConfig

from flask import Flask
from flask_cors import CORS
from src.apis.bot import bot_mod
from src.models.mongodb_schema import (
    db
)
from src.libs.simple_queue import SimpleQueueFactory


def add_api_route(api_mod):
    SystemConfig().logger.info('register api route for %s' % api_mod.name)
    app.register_blueprint(api_mod)


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

SystemConfig().logger.info('init route api')
add_api_route(bot_mod)
SystemConfig().logger.info('init connection database')
db.init_app(app)

CORS(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
