import os

os.environ['DMAI_HOME'], _ = os.path.split(os.path.abspath(__file__))

from src.common.system_config import SystemConfig

from src.libs.job import SchedulerFactory
from src.schedulers.test_scheduler import TestScheduler

if __name__ == '__main__':
    fac = SchedulerFactory(SystemConfig.logger)
    fac.add(TestScheduler())
    fac.run()
