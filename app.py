#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os

os.environ['DMAI_HOME'], _ = os.path.split(os.path.abspath(__file__))

from flask import Flask
from flask_cors import CORS
from src.apis.bot import bot_mod

app = Flask(__name__)
app.register_blueprint(bot_mod)

CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)