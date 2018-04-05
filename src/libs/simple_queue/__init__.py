import configparser
import json

import pika

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
        sq = self.queues.get(queue_name, None)
        if sq is None:
            sq = SimpleQueue(config_file_name, queue_name, call_back_function)
            self.queues[queue_name] = sq

    def get(self, queue_name):
        return self.queues.get(queue_name, None)
