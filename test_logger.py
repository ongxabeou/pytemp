import os

os.environ['DMAI_HOME'], _ = os.path.split(os.path.abspath(__file__))

from src.common.my_except import BaseMoError
from src.common.system_config import SystemConfig
from src.libs.thread_pool import ThreadPool


def __function(param1, param2, param3):
    raise BaseMoError('error')


sys_conf = SystemConfig()
pool = ThreadPool(num_workers=8, logger=sys_conf.logger)

pool.add_task(__function, 1, 2, 3)
# đợi cho đến khi tất cả nhiệm vụ được hoàn thành
pool.wait_all_tasks_done()
