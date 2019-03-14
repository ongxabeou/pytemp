import os
from functools import wraps

from src import PROJECT_NAME

os.environ[PROJECT_NAME + "_HOME"], _ = os.path.split(os.path.abspath(__file__))

from src.common.my_except import BaseMoError
from src.common.system_config import SystemConfig
from src.libs.thread_pool import ThreadPool

logger = SystemConfig().logger
pool = ThreadPool(num_workers=8, logger=logger)


def __function(param1, param2, param3):
    print(param1 + param2 + param3)
    raise BaseMoError('error')


@pool.thread
def thread_function_error(param1, param2, param3):
    print(param1 + param2 + param3)
    raise BaseMoError('error')


thread_function_error(1, 2, 3)

pool.add_task(__function, 1, 2, 3)
# đợi cho đến khi tất cả nhiệm vụ được hoàn thành
pool.wait_all_tasks_done()


# test my_except

def _try_catch_error2(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseMoError as be:
            print('error 2 %s' % be)

    return decorated


def _try_catch_error1(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseMoError as be:
            print(BaseMoError.get_track_back())
            print('error 1 %s' % be.get_message())

    return decorated


@_try_catch_error2
@_try_catch_error1
def __function():
    raise BaseMoError('text')


__function()
