from flask import Blueprint, request

from src.apis import API_URI, sys_conf, HTTP_METHOD, auth, build_response_message, try_catch_error
from src.common import SECTION
from src.controllers.bot_controller import BotController
from src.libs.http_validator import HttpValidator

bot_mod = Blueprint('bot', __name__)

log_file_name = 'BOT.PY'


# ****************Define APIS*************************
# Bot module


# @bot_mod.route(sys_conf.get_section_map(SECTION.API_URI)[API_URI.BOT_DELETE], methods=[HTTP_METHOD.DELETE])
# @auth.verify_token
# @try_catch_error
# def bot_delete(bot_id):
#     BotController(bot_id).delete()
#     return build_response_message()


@bot_mod.route(sys_conf.get_section_map(SECTION.API_URI)[API_URI.BOT_UPDATE], methods=[HTTP_METHOD.PATCH])
@auth.verify_token
@try_catch_error
def bot_update(bot_id):
    return build_response_message(BotController(bot_id).set(request.json))


@bot_mod.route(sys_conf.get_section_map(SECTION.API_URI)[API_URI.BOT_PUT], methods=[HTTP_METHOD.PUT])
@auth.verify_token
@try_catch_error
def bot_put(bot_id):
    return build_response_message(BotController(bot_id).put(request.json))


@bot_mod.route(sys_conf.get_section_map(SECTION.API_URI)[API_URI.BOT_GET], methods=[HTTP_METHOD.GET])
@auth.verify_token
@try_catch_error
def bot_get(bot_id):
    return build_response_message(BotController(bot_id).get())

# @bot_mod.route(sys_conf.get_section_map(SECTION.API_URI)[API_URI.BOT_REGISTER], methods=[HTTP_METHOD.POST])
# @auth.verify_token
# @try_catch_error
# def bot_register(bot_id):
#     return build_response_message(BotController(bot_id).register(request.data))
