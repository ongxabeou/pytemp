#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2018/03/20

    Subcrible là một thu viện hỗ trợ một tác vụ xử lý muốn loan báo cho nhiều tác cụ khác xử lý
    xử lý các yêu cầu nằm ngoài nhiệm vụ cảu tác vụ đó

    Subcrible hoạt động giống cơ chế của Chain of Responsibility Pattern. Mọi đăng ký do người chuyển nhượng(assigner)
    thu nhận sau đó gửi yêu cầu đến cho tất cả nhưng người thực thi(performer).performer kiểm tra tác vụ(task) đó có
    phải thuộc trách nhiệm của mình không, nếu phải thì thực thi ngược lại thì bỏ qua.
"""
from abc import abstractmethod
from functools import wraps

from src.libs.singleton import Singleton
from src.libs.thread_pool import ThreadPool


def subscribe(label=None, entity_id_index=0):
    """
    # >>> @subscribe('f', 0)
    # ... def f(x):
    # ...    print "Calling f(" + str(x) + ")"
    # ...    return x
    # >>> f(3)
    # Calling f(3)
    # 3
    # >>> f(3)
    # 3
    """
    def wrapper(func):
        return SubscribeFunction(func, label, entity_id_index)

    return wrapper


def subscribe_class(label=None, entity_id_index=0):
    """
    # >>> @subscribe('f', 0)
    # ... def f(x):
    # ...    print "Calling f(" + str(x) + ")"
    # ...    return x
    # >>> f(3)
    # Calling f(3)
    # 3
    # >>> f(3)
    # 3
    """

    def wrapper(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            value = func(self, *args, **kwargs)
            name = label if label else func.__name__
            entity_id = args[entity_id_index] if len(args) > entity_id_index else None
            if entity_id is None and len(kwargs.items()) > 0:
                i = len(args)
                for key, value in kwargs.items():
                    if i == entity_id_index:
                        entity_id = value
                        break
                    i += 1
            SubscribeAssigner().give(name, entity_id, list(args), kwargs, value)
            return value
        return wrapped
    return wrapper

class SubscribeFunction:
    def __init__(self, a_function, this, label=None, entity_id_index=0):
        self.function = a_function
        self.__name__ = label if label else self.function.__name__
        self.entity_id_index = entity_id_index
        self.this = this

    def __call__(self, *args, **kwargs):
        try:
            value = self.function(*args, **kwargs)
        except TypeError as e:
            if 'missing 1 required positional argument' in str(e):
                value = self.function(self.this, *args, **kwargs)
            else:
                raise e

        entity_id = args[self.entity_id_index] if len(args) > self.entity_id_index else None
        if entity_id is None and len(kwargs.items()) > 0:
            i = len(args)
            for key, value in kwargs.items():
                if i == self.entity_id_index:
                    entity_id = value
                    break
                i += 1
        SubscribeAssigner().give(self.__name__, entity_id, list(args), kwargs, value)
        return value


class BasePerformer(object):
    @abstractmethod
    def get_capacities(self):
        """
        lấy danh sách năng lực của Performer
        :return: trả về một mảng các label
        """
        pass

    @abstractmethod
    def do(self, item):
        """
        hàm thực hiện một yêu cầu, kiểm tra item.label xem có thuộc
        trách nhiệm của mình không nếu không thì return false, ngược lại thì thực hiện tác vụ
        :param item: dữ liệu yêu cầu thực thi bao gồm
        {
            'label':nhãn để xác định trách nhiệm,
            'entity_id': giá trị của một tham số trong hàm subscribe được quan tâm,
            'args': tham số đầu vào của hàm subscribe dang list,
            'kwargs': tham số đầu vào của hàm subscribe dang dict,
            'output': giá trị trả về của hàm subscribe
        }
        :return: trả về true nếu thực hiện và False nêu không thực hiện
        """
        pass


@Singleton
class SubscribeAssigner:
    thread_pool = ThreadPool(num_workers=8)

    def __init__(self):
        self.performers = {}

    def set_logger(self, logger):
        self.thread_pool.set_logger(logger)

    def add_performer(self, performer: BasePerformer):
        self.performers[performer.__class__.__name__] = performer

    def give(self, label, entity_id, args, kwargs, output):
        data = {
            'label': label,
            'entity_id': entity_id,
            'args': args,
            'kwargs': kwargs,
            'output': output
        }
        for p in self.performers.values():
            if data['label'] in p.get_capacities():
                self._owner_run(data, p)

    @thread_pool.thread
    def _owner_run(self, item, p):
        p.do(item)


# ------------------Test------------------------
if __name__ == "__main__":
    from time import sleep


    class TestPerformer(BasePerformer):
        def get_capacities(self):
            return ['some_expensive_method']

        def do(self, item):
            raise Exception('error')
            # print(repr(item))
            # return True


    SubscribeAssigner().add_performer(TestPerformer())
    SubscribeAssigner().add_performer(TestPerformer())


    @subscribe(entity_id_index=0)
    def some_expensive_method(x):
        print("Calling some_expensive_method(" + str(x) + ")")
        return x + 200


    @subscribe(entity_id_index=0)
    def some_expensive_method2(x):
        print("Calling some_expensive_method2(" + str(x) + ")")
        return x + 23351


    some_expensive_method(12)

    some_expensive_method2(14)


    class TestCache:
        # @staticmethod
        @subscribe(label='some_expensive_method', entity_id_index=0)
        def test(self, x, y=1, z=''):
            print("TestCache::test param %s %s" % (x, z))
            return int(x) + int(y)


    tc = TestCache()
    tt = tc.test(1, 1, '3')
    tt += tc.test(2, y=1)
    tt += tc.test(3, y=1)
    print('tt=', tt)

    sleep(20)
