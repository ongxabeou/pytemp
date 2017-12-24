import os

os.environ['DMAI_HOME'], _ = os.path.split(os.path.abspath(__file__))

from src.common.my_except import BaseMoError
from src.common.system_config import SystemConfig
from src.libs.thread_pool import ThreadPool

logger = SystemConfig().logger
pool = ThreadPool(num_workers=8, logger=logger)


def __function(param1, param2, param3):
    raise BaseMoError('error')


@pool.thread
def thread_function_error(param1, param2, param3):
    raise BaseMoError('error')


thread_function_error(1, 2, 3)

pool.add_task(__function, 1, 2, 3)
# đợi cho đến khi tất cả nhiệm vụ được hoàn thành
pool.wait_all_tasks_done()
