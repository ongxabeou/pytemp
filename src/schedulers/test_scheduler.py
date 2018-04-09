# -*- coding: utf-8 -*-
import schedule
import time

from src.schedulers.base_scheduler import BaseScheduler


class TestScheduler(BaseScheduler):
    def __init__(self):
        self.msg = "TestScheduler running at %s"

    def owner_do(self):
        """
        đây là hàm sẽ thực hiện công việc của scheduler,
        hàm này sẽ được gọi tự động và tự động bắt lỗi ghi log
        """
        print(self.msg % time.time())

    def get_schedule(self):
        """
        hàm xác định thời điểm chạy của scheduler, bằng cách xử dụng thư viện schedule
        Các ví dụ hướng dẫn cách xác định thời gian chạy
        1. scheduler chỉ thực hiện công việc một lần duy nhất.
            return None
        2. scheduler sẽ thực hiện mỗi 10 phút một lần.
            return schedule.every(10).minutes.do(job)
        3. scheduler sẽ thực hiện hàng ngày vào lúc 10h 30 phút.
            return schedule.every().day.at("10:30").do(job)
        4. scheduler sẽ thực hiện sau mỗi giờ.
            return schedule.every().hour.do(job)
        5. scheduler sẽ thực hiện vào mỗi thứ 2 hàng tuần.
            return schedule.every().monday.do(job)
        6. scheduler sẽ thực hiện vào mỗi thứ 5 hàng tuần và vào lúc 13h 15'.
            return schedule.every().wednesday.at("13:15").do(job)
        """
        return schedule.every(10).minutes()
