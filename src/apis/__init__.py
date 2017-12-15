#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify

from src.common.lang_config import LANG
from src.common.my_except import BaseMoError, ParamInvalidError, InputNotFoundError, LogicSystemError
from src.common.system_config import SystemConfig
from src.libs.http_jwt_auth import HttpJwtAuth, TYPICALLY
from src.models.bot_config_repository import BotConfigRepository
from src.models import PERMITTED_STRUCTURE
from src.common import ADMIN, SECTION, LOGGING_MODE
from functools import wraps


class HTTP_METHOD:
    DELETE = 'delete'
    PATCH = 'patch'
    PUT = 'put'
    POST = 'post'
    GET = 'get'


class API_URI:
    BOT_REGISTER = 'bot_register'
    BOT_DELETE = 'bot_delete'
    BOT_UPDATE = 'bot_update'
    BOT_PUT = 'bot_put'
    BOT_GET = 'bot_get'


app = Flask(__name__)
sys_conf = SystemConfig()
auth = HttpJwtAuth()


def get_param_exception(errors):
    return ParamInvalidError(LANG.VALIDATE_ERROR, errors)


def build_response_message(data=None):
    message = BaseMoError(LANG.MESSAGE_SUCCESS).get_message()
    log_mod = sys_conf.get_section_map(SECTION.LOGGING_MODE)
    if int(log_mod[LOGGING_MODE.LOG_FOR_REQUEST_SUCCESS]) == 1:
        sys_conf.logger.debug('response: %s' % (data or message))

    return data or message


@app.errorhandler(404)
def not_found(exception=None):
    if exception is None:
        exception = InputNotFoundError(LANG.NOT_FOUND)
    return jsonify(exception.get_message()), 404


@app.errorhandler(405)
def not_allowed(exception=None):
    if exception is None:
        exception = LogicSystemError(LANG.NOT_ALLOWED)
    return jsonify(exception.get_message()), 405


@app.errorhandler(412)
def param_invalid_error(exception):
    if exception is None:
        exception = ParamInvalidError(LANG.VALIDATE_ERROR)
    return jsonify(exception.get_message()), 412


@app.errorhandler(401)
@auth.error_handler
def unauthorized():
    mo = BaseMoError(LANG.UNAUTHORIZED)
    return jsonify(mo.get_message()), 401


@app.errorhandler(500)
def internal_server_error(e=None):
    print(e)
    mo = BaseMoError(LANG.INTERNAL_SERVER_ERROR)
    return jsonify(mo.get_message()), 500


@auth.get_token
def get_local_token(token):
    try:
        if not token:
            return None
        print('%s request authenticated' % token)
        return token
    except KeyError:
        return None


@auth.is_permitted
def is_permitted(typically, jwt_token, method):
    if typically == TYPICALLY.DIGEST:
        # nếu type của Authorization là Bearer hoặc Digest
        # hệ thống tự động chuyển sang digest đây là trường
        # phải check theo thuật toán JWT.
        return False
    elif typically == TYPICALLY.BASIC:
        # trường hợp type là basic thì check api_key cơ bản
        bot_conf = BotConfigRepository()
        if method in list(bot_conf.user_permitted[PERMITTED_STRUCTURE.METHODS]):
            return True

        admin_token = sys_conf.get_section_map(ADMIN.SECTION)[ADMIN.TOKEN]

        if admin_token == jwt_token:
            return method in list(bot_conf.admin_permitted[PERMITTED_STRUCTURE.METHODS])

    return False


def try_catch_error(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return jsonify(f(*args, **kwargs)), 200
        except ParamInvalidError as pie:
            return param_invalid_error(pie)
        except InputNotFoundError as inf:
            return not_found(inf)
        except LogicSystemError as lse:
            return not_allowed(lse)
        except Exception as e:
            return internal_server_error(e)

    return decorated
