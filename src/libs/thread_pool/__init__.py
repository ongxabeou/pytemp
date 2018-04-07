#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/12/22
"""
import datetime
import hashlib
# import sys

# import traceback
from functools import wraps

from queue import Queue

from threading import Thread
import logging

import sys


class ThreadPool:
    """ Pool của Thread tiêu thụ nhiệm vụ từ một hàng đợi """

    def __init__(self, num_workers, logger=None):
        self._tasks = Queue(num_workers)
        self._results = {}
        if logger is None:
            logger = logging.getLogger('ThreadPool-Logger')
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        for _ in range(num_workers):
            self.Worker(self._tasks, logger, self._results)

    def set_logger(self, logger):
        self.Worker.logger = logger

    def add_task(self, func, *args, **kargs) -> object:
        """ Thêm một tác vụ vào hàng đợi
        :param func:
        :param args:
        :param kargs:
        :return:
        """
        self._tasks.put((func, args, kargs))
        return self.Worker.get_function_id(func, args, kargs)

    def map(self, func, args_list) -> list:
        """ Thêm một danh sách các nhiệm vụ vào hàng đợi
        :param func:
        :param args_list: danh sách tham số
        :return:
        """
        ids = []
        for args in args_list:
            ids.append(self.add_task(func, *args))
        return ids

    def wait_all_tasks_done(self):
        """ Chờ hoàn thành tất cả các nhiệm vụ trong hàng đợi """
        self._tasks.join()
        res = self._results
        self._results = {}
        return res

    def thread(self, f):
        """ chuyển hàm được gọi trở thành Thread để chạy ngầm """

        @wraps(f)
        def decorated(*args, **kargs):
            return self.add_task(f, *args, **kargs)

        return decorated

    def thread_for_class(self, f):
        @wraps(f)
        def decorated(me, *args, **kargs):
            args += me
            return self.add_task(f, *args, **kargs)

        return decorated

    class Worker(Thread):
        """ Thread thực hiện nhiệm vụ từ một hàng đợi nhiệm vụ nhất định """

        def __init__(self, tasks, logger, results):
            Thread.__init__(self)
            self.results = results
            self.tasks = tasks
            self.logger = logger
            self.daemon = True
            self.start()

        def run(self):
            """ hàm thực hiện nhiệm vụ và ghi kết quả vào result
                quá trình thực hiện nếu lỗi được ghi log nếu logger != None
            """
            while True:
                func, args, kargs = self.tasks.get()
                try:
                    func_id = self.get_function_id(func, args, kargs)
                    result = func(*args, **kargs)
                    self.results[func_id] = result
                except Exception as ex:
                    if self.logger is None:
                        print(ex)
                    else:
                        line = '=================================================================='
                        if args is ():
                            self.logger.exception('Exception in thread %s\n%s :: %s' %
                                                  (line, str(datetime.datetime.now()), func.__name__))
                        else:
                            self.logger.exception('Exception in thread %s\n%s :: %s with param %r' %
                                                  (line, str(datetime.datetime.now()), func.__name__, args))
                finally:
                    # Đánh dấu công việc này là xong, dù có ngoại lệ xảy ra hay không
                    self.tasks.task_done()

        @staticmethod
        def get_function_id(func, args, kargs=None):
            identify = "{function} {agrs} ".format(
                function=func.__name__,
                agrs="args %r kargs %r" % (args, kargs))
            return hashlib.md5(identify.encode('utf-8')).hexdigest()


# ------------------Test------------------------
if __name__ == "__main__":
    from random import randrange
    from time import sleep

    # Khởi chạy một ThreadPool với 8 công nhân(Worker)
    # giao cho 8 công nhân đó 16 nhiệm vụ, các công nhân
    # nhận nhiệm vụ theo cơ chế hàng đợi(FIFO). chương trình
    # sẽ đợi cho đến khi tất cả các nhiệm vụ được hoàn thành.
    t_pool = ThreadPool(num_workers=8)


    def wait_delay(id_w, time):
        # Chức năng được thực hiện trong một chủ đề
        print("(%d)id sleeping for (%d)sec" % (id_w, time))
        sleep(1)
        return time * 100


    @t_pool.thread
    def wait_delay2(time):
        print("wait_delay2 sleeping for (%d)sec" % time)
        sleep(int(time))


    @t_pool.thread
    def func_error2(time):
        print("func_error2 sleeping for (%d)sec" % time)
        sleep(0.1)
        raise Exception("error2 in thread")


    def func_error():
        raise Exception("error in thread")


    # gọi hàm đã chuyển thành thread trương chình không
    # chờ xử lý xong mà vẫn sẽ đi tiếp
    wait_delay2(2)

    # Tạo sự chậm trễ ngẫu nhiên cho 15 nhiệm vụ.
    # một nhiệm vụ bao gồm mã và thời gian hoàn thành.
    t_delays = [(i + 1, randrange(3, 7)) for i in range(15)]

    # Thêm các công việc với số lượng lớn vào thread.
    # Hoặc bạn có thể sử dụng `pool.add_task` để thêm
    # các công việc đơn lẻ.
    t_func_ids = t_pool.map(wait_delay, t_delays)
    # thêm một nhiệm vụ đơn lẻ
    t_func_id = t_pool.add_task(wait_delay, 16, 8)

    # đợi cho đến khi tất cả nhiệm vụ được hoàn thành
    t_results = t_pool.wait_all_tasks_done()
    # kiểm tra kết quả
    for t_id in t_func_ids:
        print('function %s result %r' % (t_id, t_results[t_id]))
    print('function %s result %r' % (t_func_id, t_results[t_func_id]))

    # gọi hàm có lỗi
    func_error2(1)
    t_pool.add_task(func_error)

    sleep(1)
