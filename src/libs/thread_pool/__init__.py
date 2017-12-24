#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/12/22
"""
import datetime
import sys

# để có thể chạy được cho cả python 2 và 3
import traceback
from functools import wraps

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue

from threading import Thread


class Worker(Thread):
    """ Thread thực hiện nhiệm vụ từ một hàng đợi nhiệm vụ nhất định """

    def __init__(self, tasks, logger):
        Thread.__init__(self)
        self.tasks = tasks
        self.logger = logger
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except:
                # Một trường hợp ngoại lệ đã xảy ra trong thread này
                if self.logger is None:
                    traceback.print_exc(file=sys.stdout)
                else:
                    line = '=================================================================='
                    if args is ():
                        self.logger.exception('%s\n%s :: %s exception occurred' %
                                              (line, str(datetime.datetime.now()), func.__name__))
                    else:
                        self.logger.exception('%s\n%s :: %s exception occurred with param %r' %
                                              (line, str(datetime.datetime.now()), func.__name__, args))
            finally:
                # Đánh dấu công việc này là xong, dù có ngoại lệ xảy ra hay không
                self.tasks.task_done()


class ThreadPool:
    """ Pool của Thread tiêu thụ nhiệm vụ từ một hàng đợi """

    def __init__(self, num_workers, logger=None):
        self.tasks = Queue(num_workers)
        for _ in range(num_workers):
            Worker(self.tasks, logger)

    def add_task(self, func, *args, **kargs):
        """ Thêm một tác vụ vào hàng đợi """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Thêm một danh sách các nhiệm vụ vào hàng đợi """
        for args in args_list:
            self.add_task(func, *args)

    def wait_all_tasks_done(self):
        """ Chờ hoàn thành tất cả các nhiệm vụ trong hàng đợi """
        self.tasks.join()

    def thread(self, f):
        """ chuyển hàm được gọi trở thành Thread để chạy ngầm """

        @wraps(f)
        def decorated(*args, **kargs):
            self.add_task(f, *args, **kargs)

        return decorated


# ------------------Test------------------------
if __name__ == "__main__":
    from random import randrange
    from time import sleep

    # Khởi chạy một ThreadPool với 8 công nhân(Worker)
    # giao cho 8 công nhân đó 16 nhiệm vụ, các công nhân
    # nhận nhiệm vụ theo cơ chế hàng đợi(FIFO). chương trình
    # sẽ đợi cho đến khi tất cả các nhiệm vụ được hoàn thành.
    pool = ThreadPool(num_workers=8)


    # Chức năng được thực hiện trong một chủ đề
    def wait_delay(id_w, time):
        print("(%d)id sleeping for (%d)sec" % (id_w, time))
        sleep(time)


    @pool.thread
    def wait_delay2(time):
        print("wait_delay2 sleeping for (%d)sec" % time)
        sleep(time)


    @pool.thread
    def func_error2(time):
        print("func_error2 sleeping for (%d)sec" % time)
        sleep(time)
        raise Exception("error2 in thread")


    def func_error():
        raise Exception("error in thread")


    # gọi hàm đã chuyển thành thread trương chình không
    # chờ xử lý xong mà vẫn sẽ đi tiếp
    wait_delay2(10)
    # gọi hàm có lỗi
    func_error2(10)

    # Tạo sự chậm trễ ngẫu nhiên cho 15 nhiệm vụ.
    # một nhiệm vụ bao gồm mã và thời gian hoàn thành.
    delays = [(i + 1, randrange(3, 7)) for i in range(15)]

    # Thêm các công việc với số lượng lớn vào thread.
    # Hoặc bạn có thể sử dụng `pool.add_task` để thêm
    # các công việc đơn lẻ.
    pool.map(wait_delay, delays)
    # thêm một nhiệm vụ đơn lẻ
    pool.add_task(wait_delay, 16, 8)

    pool.add_task(func_error)
    # đợi cho đến khi tất cả nhiệm vụ được hoàn thành
    pool.wait_all_tasks_done()
