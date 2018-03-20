#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""
from abc import abstractmethod
from functools import wraps
from flask import make_response, request
from werkzeug.datastructures import Authorization
from jose import jwt


class TYPICALLY:
    BASIC = 'Basic'
    BEARER = 'Bearer'
    DIGEST = 'Digest'


class ProjectAuthorization:
    def __init__(self):
        self.key = None
        self.algorithm = None
        self.options = {'verify_signature': True,
                        'verify_aud': False,
                        'verify_iat': False,
                        'verify_exp': False,
                        'verify_nbf': False,
                        'verify_iss': False,
                        'verify_sub': False,
                        'verify_jti': False,
                        }

    @abstractmethod
    def verify_token(self, jwt_token, typically):
        pass

    @abstractmethod
    def is_permitted(self, jwt_token, typically, method):
        pass

    def encode(self, body):
        try:
            return jwt.encode(body, self.key, self.algorithm)
        except Exception as e:
            print('can not encode token: %s' % e)
            return None

    def decode(self, body):
        try:
            return jwt.decode(body, self.key, self.algorithm, self.options)
        except Exception as e:
            print('can not decode token: %s' % e)
            return None


class HttpJwtAuth(object):
    def __init__(self, project_auth: ProjectAuthorization, scheme=None, realm=None):
        # ProjectAuthorization do project cụ thể sẽ cài đặt phương thức authen của project đó.
        self.project_auth = project_auth
        self.scheme = [scheme] or [TYPICALLY.BASIC.lower(), TYPICALLY.DIGEST.lower(), TYPICALLY.BEARER.lower()]
        self.realm = realm or "Authentication Required"
        self.auth_error_callback = None

        def default_auth_error():
            return "Unauthorized Access"

        self.error_handler(default_auth_error)

    def error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            result = make_response(result)
            if result.status_code == 200:
                # nếu người dùng không set status code thì set cho nó là 401
                result.status_code = 401
            if 'WWW-Authenticate' not in result.headers.keys():
                # nếu chưa set response trả về cho trường hợp Authenticate thì set mới cho nó
                result.headers['WWW-Authenticate'] = self.authenticate_header()
            return result

        self.auth_error_callback = decorated
        return decorated

    def authenticate_header(self):
        return '{0} realm="{1}"'.format(self.scheme, self.realm)

    def verify_token(self, f):
        method = f.__name__

        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.authorization
            token = None
            auth_type = None
            # link jwt: https://jwt.io/introduction/
            if auth is None and 'Authorization' in request.headers:
                # Flask/Werkzeug không công nhận bất kỳ loại authentication
                # nào khác ngoài Basic or Digest, vì vậy cần chuyển đối tượng
                # bằng tay
                try:
                    auth_type, token = request.headers['Authorization'].split(None, 1)
                    local_auth_type = TYPICALLY.DIGEST if auth_type == TYPICALLY.BEARER else auth_type
                    auth = Authorization(local_auth_type, {'token': token})
                except ValueError:
                    # Authorization header là rỗng hoặc không có mã thông báo
                    pass

            # nếu kiểu auth không khớp, chúng ta hành động như thể không có auth
            # này là tốt hơn so với thất bại trực tiếp, vì nó cho phép callback
            # để xử lý các trường hợp đặc biệt, như hỗ trợ nhiều kiểu auth
            if auth is not None and auth.type.lower() in self.scheme:
                auth = None

            # Flask thường giải quyết các yêu cầu của OPTIONS riêng, nhưng trong
            # trường hợp nó được cấu hình để chuyển tiếp các ứng dụng, chúng tôi
            # cần bỏ qua tiêu đề xác thực và để cho yêu cầu thông qua
            # để tránh những tương tác không mong muốn với CORS.
            if request.method != 'OPTIONS':  # pragma: no cover
                if auth:
                    if not self.authenticate(str(auth_type), token, method):
                        # Xóa bộ đệm TCP nhận được dữ liệu đang chờ xử lý
                        print('authenticate for token %s api_name  %s error %s' % (
                            token, method, str(request.data)[0]))
                        return self.auth_error_callback()
                else:
                    return self.auth_error_callback()
            return f(*args, **kwargs)

        return decorated_function

    def authenticate(self, auth_type, token, method):
        if self.project_auth is None:
            raise NotImplementedError('developer must implement for ProjectAuthorization class')
        local_token = self.project_auth.verify_token(token, auth_type)
        if local_token:
            return self.project_auth.is_permitted(token, auth_type, method)
        else:
            return False


# --------------------------- TEST ---------------------------
if __name__ == '__main__':

    def try_catch_error2(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                print('ok 2')
                return f(*args, **kwargs)
            except Exception as e:
                print('try_catch_error2', e)

        return decorated


    def try_catch_error1(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                print('ok 1')
                return f(*args, **kwargs)
            except Exception as e:
                print('try_catch_error1', e)

        return decorated


    @try_catch_error2
    @try_catch_error1
    def func():
        raise Exception('error')


    func(10)
