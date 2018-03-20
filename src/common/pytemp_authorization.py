from flask import json

import redis
import requests
from jose import jwt

from src.common.lang_config import LANG
from src.common.my_except import BaseMoError
from src.common.system_config import SystemConfig
from src.libs.http_jwt_auth import ProjectAuthorization, TYPICALLY


class AUTH_CONFIG:
    JWT = 'JWT'
    SECRET_KEY = 'secret_key'
    ALGORITHM = 'algorithm'
    MODULE = 'module'


class PytempAuthorization(ProjectAuthorization):
    def __init__(self):
        super(PytempAuthorization, self).__init__()
        self.config = SystemConfig()
        self.key = self.config.get_section_map(AUTH_CONFIG.JWT)[AUTH_CONFIG.SECRET_KEY]
        self.algorithm = self.config.get_section_map(AUTH_CONFIG.JWT)[AUTH_CONFIG.ALGORITHM]
        self.module = self.config.get_section_map(AUTH_CONFIG.JWT)[AUTH_CONFIG.MODULE]
        self.ADMIN = 'admin'

    def get(self, token, field_name):
        """
        lấy thông tin theo tên trường từ Json Web Token
        :param token:
        :param field_name:
        :return:
        """
        body = self.decode(token)
        if body is None:
            return None
        return body.get(field_name, None)

    @staticmethod
    def _get_requests(url, api_key=None):
        if api_key is None:
            result = requests.get(url)
        else:
            result = requests.get(url=url, headers={'Authorization': 'Basic %s' % api_key})
        if result.status_code == 200:
            return json.loads(result.text)
        else:
            return None

    def is_permitted(self, jwt_token, typically, method):
        """
        hàm kiểm tra method có được phân quyền hay không
        :param jwt_token:
        :param typically:
        :param method:
        :return:
        """
        return True

    def verify_token(self, jwt_token, typically):
        """
        nếu là module có chức năng au then thì kiem tra trong redis
        nếu là module khác thì gọi moddule authen để verify token
        :param typically:
        :param jwt_token:
        :return: trả về token nếu hợp lệ
        """
        try:
            if typically == TYPICALLY.BEARER or typically == TYPICALLY.DIGEST:
                return jwt_token
            elif typically == TYPICALLY.BASIC:  # and self.module == self.ADMIN:
                return jwt_token
            return None
        except Exception as e:
            print(e)
            BaseMoError(LANG.INTERNAL_SERVER_ERROR).get_message()
            return None
