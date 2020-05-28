import datetime
import time
from functools import wraps

PROF_DATA = {}


def per_meter(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling


def fprint_info(*args, error=False):
    elapsed_time = time.time()
    now = datetime.datetime.fromtimestamp(elapsed_time)
    if error:
        print('error::[%s]' % now, *args)
    else:
        print('info::[%s]' % now, *args)


def fprint_error(*args):
    elapsed_time = time.time()
    now = datetime.datetime.fromtimestamp(elapsed_time)
    print('error::[%s]' % now, *args)


class PerformanceMeter:
    @staticmethod
    def print_prof_data():
        for f_name, data in PROF_DATA.items():
            max_time = max(data[1])
            avg_time = sum(data[1]) / len(data[1])
            print("Function %s called %d times. " % (f_name, data[0]))
            print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))

    @staticmethod
    def clear_prof_data():
        global PROF_DATA
        PROF_DATA = {}


# ------------------Test------------------------
if __name__ == "__main__":
    fprint_info("Function %s called %d times. " % ('aev', 123), "văvwe", 13516, error=False)


    @per_meter
    def load_test(during_time):
        time.sleep(during_time)
        print("sleep: ", during_time, 'seconds')


    for i in range(3):
        load_test(1)

    PerformanceMeter.print_prof_data()
    PerformanceMeter.clear_prof_data()
