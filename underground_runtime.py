import os

from src.schedulers.scheduler_factory import SchedulerFactory

os.environ['SM_HOME'], _ = os.path.split(os.path.abspath(__file__))

from src.schedulers.test_scheduler import TestScheduler

if __name__ == '__main__':
    fac = SchedulerFactory()
    fac.add(TestScheduler())
    fac.run()
