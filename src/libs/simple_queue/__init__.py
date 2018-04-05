#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2018/03/20

    SimpleQueue là thư viện hỗ trợ việc quả lý các RabitMQ thông qua một SimpleQueueFactory
    để bảo đảm các connection vào RabitMQ được tối ưu bằng cách tái xử dụng lại cho mỗi lần push.
"""

import configparser
import json
from functools import wraps

import pika
import time

from src.libs.singleton import Singleton


class QUEUE_MODE:
    HOST = 'host'
    PORT = 'port'
    USER = 'user'
    PASSWORD = 'password'


class SimpleQueue:
    def __init__(self, config_file_name, queue_name, call_back_function=None):
        self._sections = {}
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name, 'utf-8')
        self.queue_name = queue_name
        self._create_connection()
        self._call_back = call_back_function

    def _create_connection(self):
        host = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.HOST]
        port = int(self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.PORT])
        user_name = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.USER]
        password = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.PASSWORD]
        credentials = pika.PlainCredentials(user_name, password)
        parameters = pika.ConnectionParameters(host, port, '/', credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        if self._call_back:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(self._call_back, queue=self.queue_name)
            self.channel.start_consuming()

    def _get_section_map(self, section):
        if section in self._sections:
            return self._sections[section]
        local_dic = {}
        options = self.config.options(section)
        for option in options:
            try:
                local_dic[option] = self.config.get(section, option)
                if local_dic[option] == -1:
                    print("skip: %s" % option)
            except Exception as ex:
                print("get section of SystemConfig %s option %s have error:%s!" % (section, option, ex))
                local_dic[option] = None
        self._sections[section] = local_dic
        return local_dic

    def push(self, message):
        success = False
        print(" [x] Sent %r" % message)
        try_push = 3
        while not success and try_push > 0:
            success = self._owner_push(message)
            if not success:
                time.sleep(0.1)
                self.connection.close()
                self._create_connection()
                try_push -= 1

        if not success:
            raise KeyError('can not push message to queue [%s]', self.queue_name)

    def _owner_push(self, message):
        return self.channel.basic_publish(exchange='',
                                          routing_key=self.queue_name,
                                          body=json.dumps(message),
                                          properties=pika.BasicProperties(content_type='text/plain',
                                                                          delivery_mode=2,  # make message persistent
                                                                          ))


@Singleton
class SimpleQueueFactory:
    def __init__(self):
        self.queues = {}

    def add(self, config_file_name, queue_name, call_back_function=None):
        """
        hàm tạo một kết nối đến RabitMQ và đưa vào kho quản lý
        :param config_file_name:
        :param queue_name:
        :param call_back_function:
        :return:
        """
        sq = self.queues.get(queue_name, None)
        if sq is None:
            sq = SimpleQueue(config_file_name, queue_name, call_back_function)
            self.queues[queue_name] = sq
        return sq

    def get(self, queue_name):
        try:
            return self.queues[queue_name]
        except KeyError:
            raise KeyError('you must add queue[%s] into factory before get queue' % queue_name)

    def push_to_queue(self, queue_name):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                value = func(*args, **kwargs)
                sq = self.queues.get(queue_name)
                sq.push(value)
                return value

            return wrapped

        return wrapper

    def push_to_queue_for_class(self, queue_name):
        def wrapper(func):
            @wraps(func)
            def wrapped(my_self, *args, **kwargs):
                value = func(my_self, *args, **kwargs)
                sq = self.queues.get(queue_name)
                sq.push(value)
                return value

            return wrapped

        return wrapper


# ------------------Test------------------------
if __name__ == '__main__':
    # hướng dẫn cách dùng Simple Queue
    # tạo đối tượng queue
    sqf = SimpleQueueFactory()
    # 'đường dẫn đến file câu hình của project' và tên queue
    sqf.add('../../../resources/configs/dmai.conf', 'queue_name')
    # lấy queue để sử dụng
    t_sq = SimpleQueueFactory().get('queue_name')
    # đẩy một item vào queue
    t_sq.push("message")

    @sqf.push_to_queue('queue_name')
    def test_msg():
        return 'test_msg'


    print(test_msg())


    class TestClass:
        msq = 'test_msg_class'

        @sqf.push_to_queue_for_class('queue_name')
        def test_msg(self):
            return self.msq


    print(TestClass().test_msg())
