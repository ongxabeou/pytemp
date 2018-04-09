from src.common.system_config import SystemConfig
from src.libs.singleton import Singleton
from src.libs.thread_pool import ThreadPool
from src.schedulers.base_scheduler import BaseScheduler
import schedule
import time


@Singleton
class SchedulerFactory:

    thread_pool = ThreadPool(num_workers=8)

    def __init__(self):
        self.schedulers = {}
        self.tasks = {}
        self.logger = SystemConfig().logger

    def add(self, scheduler: BaseScheduler, scheduler_name=None):
        name = scheduler_name if scheduler_name else scheduler.__class__.__name__
        sq = self.schedulers.get(name, None)
        if sq is None:
            scheduler.set_logger(self.logger)
            the_schedule = scheduler.get_schedule()
            if the_schedule:
                the_schedule.do(scheduler.do)
                self.schedulers[name] = scheduler
            else:
                self.tasks[name] = scheduler
            return scheduler
        return sq

    def run(self):
        for stack in self.tasks.values():
            self.owner_run_scheduler(stack)

        while True:
            schedule.run_pending()
            time.sleep(1)

    @thread_pool.thread
    def owner_run_scheduler(self, scheduler: BaseScheduler):
        scheduler.do()
