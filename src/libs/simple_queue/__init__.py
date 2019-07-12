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
import queue
import time
from functools import wraps

import pika

from src.libs.singleton import Singleton
from src.libs.thread_pool import ThreadPool


class QUEUE_MODE:
    HOST = 'host'
    PORT = 'port'
    USER = 'user'
    PASSWORD = 'password'


_thread_pool_for_local_queue = ThreadPool(num_workers=8)


class SimpleQueue:
    def __init__(self, queue_name, config_file_name=None, config_params=None, call_back_function=None):
        self._sections = {}
        self.config_params = {}
        if call_back_function is None:
            raise KeyError('you must implement for call_back_function to get data if queue have new item')
        if config_file_name:
            self.config = configparser.ConfigParser()
            self.config.read(config_file_name, 'utf-8')
            self.config_params[QUEUE_MODE.HOST] = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.HOST]
            self.config_params[QUEUE_MODE.PORT] = int(self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.PORT])
            self.config_params[QUEUE_MODE.USER] = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.USER]
            self.config_params[QUEUE_MODE.PASSWORD] = self._get_section_map(QUEUE_MODE.__name__)[QUEUE_MODE.PASSWORD]
        if config_params:
            self.config_params[QUEUE_MODE.HOST] = config_params[QUEUE_MODE.HOST]
            self.config_params[QUEUE_MODE.PORT] = config_params[QUEUE_MODE.PORT]
            self.config_params[QUEUE_MODE.USER] = config_params[QUEUE_MODE.USER]
            self.config_params[QUEUE_MODE.PASSWORD] = config_params[QUEUE_MODE.PASSWORD]

        self.local_queue = None
        self.queue_name = queue_name
        self._call_back = call_back_function
        # trường hợp dùng local_queue
        if config_file_name is None and config_params is None:
            self.local_queue = queue.Queue()
            self._local_consume()
        else:
            self._create_connection()

    def size(self):
        if self.local_queue:
            return self.local_queue.qsize()

        if self.foreign_queue:
            return self.foreign_queue.method.message_count

    def _isinstance(self):
        return isinstance(self, SimpleQueue)

    def _create_connection(self):
        if self.local_queue is None:
            host = self.config_params[QUEUE_MODE.HOST]
            port = int(self.config_params[QUEUE_MODE.PORT])
            user_name = self.config_params[QUEUE_MODE.USER]
            password = self.config_params[QUEUE_MODE.PASSWORD]
            credentials = pika.PlainCredentials(user_name, password)
            parameters = pika.ConnectionParameters(host, port, '/', credentials)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.foreign_queue = self.channel.queue_declare(queue=self.queue_name, durable=True)

            if self._call_back is not None:
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(self._call_back, queue=self.queue_name)

    @_thread_pool_for_local_queue.thread
    def _local_consume(self):
        while True:
            item = self.local_queue.get()
            self._call_back(item)

    def start(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()

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
        if self.local_queue is None:
            success = False
            print(" [x] Sent %r" % message)
            try_push = 3
            while not success and try_push > 0:
                try:
                    success = self._owner_push(message)
                    if not success:
                        time.sleep(0.1)
                        self.connection.close()
                        self._create_connection()
                        try_push -= 1
                except Exception as e:
                    print(e)
                    success = False
                    try_push -= 1
            if not success:
                raise KeyError('can not push message to queue [%s]', self.queue_name)
        else:
            self.local_queue.put(message)

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

    def add(self, queue_name, config_file_name=None, config_params=None, call_back_function=None):
        """
        hàm tạo một kết nối đến RabitMQ và đưa vào kho quản lý
        :param config_params:
        :param config_file_name:
        :param queue_name:
        :param call_back_function:
        :return:
        """
        sq = self.queues.get(queue_name, None)
        if sq is None:
            sq = SimpleQueue(queue_name, config_file_name, config_params, call_back_function)
            self.queues[queue_name] = sq
        return sq

    def get(self, queue_name) -> SimpleQueue:
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

    def push(self, queue_name, item):
        sq = self.queues.get(queue_name)
        sq.push(item)


# ------------------Test------------------------
if __name__ == '__main__':
    def process_message_callback(item):
        print(item)


    # hướng dẫn cách dùng Simple Queue
    # tạo đối tượng queue
    sqf = SimpleQueueFactory()
    # 'đường dẫn đến file câu hình của project' và tên queue
    sqf.add(queue_name='foo',
            call_back_function=process_message_callback)
    # lấy queue để sử dụng
    t_sq = SimpleQueueFactory().get('foo')
    # đẩy một item vào queue
    t_sq.push("message 1")


    @sqf.push_to_queue('foo')
    def test_msg():
        return 'message 2'


    test_msg()


    class TestClass:
        msq = 'message 3'

        @sqf.push_to_queue_for_class('foo')
        def test_msg(self):
            return self.msq


    TestClass().test_msg()

    print('queue size::', sqf.get('foo').size())
    time.sleep(1)
    print('queue size::', sqf.get('foo').size())
