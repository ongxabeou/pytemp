#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28

    LRU viết tắt của từ least recently used. là thư viện hỗ trợ cache
    lại các kết quả xử lý của nhưng lần sử dụng gần nhất.
    LRU Cache sẽ lưu lại trên RAM hoặc Redis
"""
import configparser
from collections import OrderedDict
import time
import threading
import weakref

import redis

from src.libs.singleton import Singleton


class STORE_TYPE:
    LOCAL = 1
    REDIS = 2


CACHE_MAX_SIZE_DEFAULT = 1024000
EXPIRATION_DEFAULT = 15 * 60


def lru_cache_function(prefix_key=None, max_size=CACHE_MAX_SIZE_DEFAULT,
                       expiration=EXPIRATION_DEFAULT,
                       store_type=STORE_TYPE.LOCAL,
                       config_file_name=None):
    """
    >>> @lru_cache_function(3, 1)
    ... def f(x):
    ...    print "Calling f(" + str(x) + ")"
    ...    return x
    >>> f(3)
    Calling f(3)
    3
    >>> f(3)
    3
    """

    def wrapper(func):
        if store_type == STORE_TYPE.LOCAL:
            return LRUCachedFunction(func, prefix_key, LRUCacheDict(max_size, expiration))
        elif store_type == STORE_TYPE.REDIS:
            if config_file_name is None:
                raise ValueError('config_file_name must not be None if store_type is REDIS')
            return LRUCachedFunction(func, prefix_key, RedisCacheDict(config_file_name, max_size, expiration))
        else:
            raise NotImplementedError('store_type=%s' % store_type)

    return wrapper


class LRUCachedFunction(object):
    """
    Một chức năng ghi nhớ, được hỗ trợ bởi một bộ nhớ cache LRU.

    >>> def f(x):
    ...    print "Calling f(" + str(x) + ")"
    ...    return x
    >>> f = LRUCachedFunction(f, LRUCacheDict(max_size=3, expiration=3) )
    >>> f(3)
    Calling f(3)
    3
    >>> f(3)
    3
    >>> import time
    >>> time.sleep(4) #Cache should now be empty, since expiration time is 3.
    >>> f(3)
    Calling f(3)
    3
    >>> f(4)
    Calling f(4)
    4
    >>> f(5)
    Calling f(5)
    5
    >>> f(3) #Still in cache, so no print statement. At this point, 4 is the least recently used.
    3
    >>> f(6)
    Calling f(6)
    6
    >>> f(4) #No longer in cache - 4 is the least recently used, and there are at least 3 others
    # items in cache [3,4,5,6].
    Calling f(4)
    4

    """

    def __init__(self, a_function, prefix_key=None, cache=None, store_type=STORE_TYPE.LOCAL, config_file_name=None):
        if cache:
            self.cache = cache
        else:
            if store_type == STORE_TYPE.LOCAL:
                self.cache = LRUCacheDict()
            elif store_type == STORE_TYPE.REDIS:
                if config_file_name is None:
                    raise ValueError('config_file_name must not be None if store_type is REDIS')
                self.cache = RedisCacheDict(config_file_name)
            else:
                raise NotImplementedError('store_type=%s' % store_type)
        self.function = a_function
        self.__name__ = prefix_key if prefix_key else self.function.__name__

    def __call__(self, *args, **kwargs):
        # Về nguyên tắc một repr python (...) không nên trả về bất kỳ ký tự '#'.
        key = self.__name__ + "#" + repr((args, kwargs))

        try:
            # print("cache key", key)
            return self.cache[key]
        except KeyError:
            try:
                value = self.function(*args, **kwargs)
            except TypeError as e:
                if 'missing 1 required positional argument' in str(e):
                    value = self.function(0, *args, **kwargs)
                else:
                    raise e
            self.cache[key] = value
            return value


def _lock_decorator(func):
    """
    If the LRUCacheDict is concurrent, then we should lock in order to avoid
    conflicts with threading, or the ThreadTrigger.
    """

    def withlock(self, *args, **kwargs):
        if self.concurrent:
            with self._rlock:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    # withlock.__name__ == func.__name__
    return withlock


class LRUCacheDict(object):
    """ A dictionary-like object, supporting LRU caching semantics.

    >>> d = LRUCacheDict(max_size=3, expiration=3)
    >>> d['foo'] = 'bar'
    >>> d['foo']
    'bar'
    >>> import time
    >>> time.sleep(4) # 4 seconds > 3 second cache expiry of d
    >>> d['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'
    >>> d['a'] = 'A'
    >>> d['b'] = 'B'
    >>> d['c'] = 'C'
    >>> d['d'] = 'D'
    >>> d['a'] # Should return value error, since we exceeded the max cache size
    Traceback (most recent call last):
        ...
    KeyError: 'a'

    By default, this cache will only expire items whenever you poke it - all methods on
    this class will result in a cleanup. If the thread_clear option is specified, a background
    thread will clean it up every thread_clear_min_check seconds.

    If this class must be used in a multithreaded environment, the option concurrent should be
    set to true. Note that the cache will always be concurrent if a background cleanup thread
    is used.
    """

    def __init__(self, max_size=CACHE_MAX_SIZE_DEFAULT, expiration=EXPIRATION_DEFAULT,
                 thread_clear=False,
                 concurrent=False):
        self.max_size = max_size
        self.expiration = expiration
        self.__values = {}
        self.__expire_times = OrderedDict()
        self.__access_times = OrderedDict()
        self.thread_clear = thread_clear
        self.concurrent = concurrent or thread_clear
        if self.concurrent:
            self._rlock = threading.RLock()
        if thread_clear:
            et = self.EmptyCacheThread(self)
            et.start()

    class EmptyCacheThread(threading.Thread):
        daemon = True

        def __init__(self, cache, peek_duration=60):
            # me = self
            #
            # def kill_self(o):
            #     me
            self.ref = weakref.ref(cache)
            self.peek_duration = peek_duration
            super(LRUCacheDict.EmptyCacheThread, self).__init__()

        def run(self):
            while self.ref():
                c = self.ref()
                if c:
                    next_expire = c.cleanup()
                    if next_expire is None:
                        time.sleep(self.peek_duration)
                    else:
                        time.sleep(next_expire + 1)
                        # c = None

    @_lock_decorator
    def size(self):
        return len(self.__values)

    @_lock_decorator
    def clear(self):
        """
        Clears the dict.

        >>> d = LRUCacheDict(max_size=3, expiration=1)
        >>> d['foo'] = 'bar'
        >>> d['foo']
        'bar'
        >>> d.clear()
        >>> d['foo']
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        """
        self.__values.clear()
        self.__expire_times.clear()
        self.__access_times.clear()

    def __contains__(self, key):
        return key in self.__values

    @_lock_decorator
    def has_key(self, key):
        """
        This method should almost NEVER be used. The reason is that between the time
        has_key is called, and the key is accessed, the key might vanish.

        You should ALWAYS use a try: ... except KeyError: ... block.

        >>> d = LRUCacheDict(max_size=3, expiration=1)
        >>> d['foo'] = 'bar'
        >>> d['foo']
        'bar'
        >>> import time
        >>> if d.has_key('foo'):
        ...    time.sleep(2) #Oops, the key 'foo' is gone!
        ...    d['foo']
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        """
        return key in self.__values

    @_lock_decorator
    def __setitem__(self, key, value):
        t = int(time.time())
        self.__delete__(key)
        self.__values[key] = value
        self.__access_times[key] = t
        self.__expire_times[key] = t + self.expiration
        self.cleanup()

    @_lock_decorator
    def __getitem__(self, key):
        t = int(time.time())
        del self.__access_times[key]
        self.__access_times[key] = t
        self.cleanup()
        return self.__values[key]

    @_lock_decorator
    def __delete__(self, key):
        if key in self.__values:
            del self.__values[key]
            del self.__expire_times[key]
            del self.__access_times[key]

    @_lock_decorator
    def cleanup(self):
        if self.expiration is None:
            return None
        t = int(time.time())
        # Delete expired
        next_expire = None
        for k in self.__expire_times:
            if self.__expire_times[k] < t:
                self.__delete__(k)
            else:
                next_expire = self.__expire_times[k]
                break

        # If we have more than self.max_size items, delete the oldest
        while len(self.__values) > self.max_size:
            for k in self.__access_times:
                self.__delete__(k)
                break
        if not (next_expire is None):
            return next_expire - t
        else:
            return None


class REDIS_MODE:
    HOST = 'host'
    PORT = 'port'
    EXPIRED_TIME_FOR_KEY = 'expired_time_for_key'


# [chú ý] RedisCacheDict là Singleton nhằm đẩy nhanh tốc độ khởi tạo của đối tượng này.
# Tuy nhiên chưa chắc Singleton có ảnh hưởng gì đến hệ thống hay không, cần theo
# dõi trong quá trình sử dụng thục tế để xác định.
@Singleton
class RedisCacheDict(object):
    """ A dictionary-like object, supporting LRU caching semantics.

    >>> d = RedisCacheDict(max_size=3, expiration=3)
    >>> d['foo'] = 'bar'
    >>> d['foo']
    'bar'
    >>> import time
    >>> time.sleep(4) # 4 seconds > 3 second cache expiry of d
    >>> d['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'
    >>> d['a'] = 'A'
    >>> d['b'] = 'B'
    >>> d['c'] = 'C'
    >>> d['d'] = 'D'
    >>> d['a'] # Should return value error, since we exceeded the max cache size
    Traceback (most recent call last):
        ...
    KeyError: 'a'

    By default, this cache will only expire items whenever you poke it - all methods on
    this class will result in a cleanup. If the thread_clear option is specified, a background
    thread will clean it up every thread_clear_min_check seconds.

    If this class must be used in a multithreaded environment, the option concurrent should be
    set to true. Note that the cache will always be concurrent if a background cleanup thread
    is used.
    """

    def __init__(self, config_file_name, max_size=CACHE_MAX_SIZE_DEFAULT, expiration=CACHE_MAX_SIZE_DEFAULT):
        self.max_size = max_size
        self.expiration = expiration
        config = configparser.ConfigParser()
        config.read(config_file_name, 'utf-8')
        self.host = config.options(REDIS_MODE.__name__)[REDIS_MODE.HOST]
        self.port = config.options(REDIS_MODE.__name__)[REDIS_MODE.PORT]
        self._redis = redis.Redis(host=self.host, port=self.port, db=0)

    @_lock_decorator
    def size(self):
        return self._redis.dbsize()

    @_lock_decorator
    def clear(self):
        """
        Clears the dict. Không thực hiện do trong Redis có thể dùng chung nhiều dự án
        """
        pass

    def __contains__(self, key):
        return self._redis.exists(key)

    @_lock_decorator
    def has_key(self, key):
        """
        This method should almost NEVER be used. The reason is that between the time
        has_key is called, and the key is accessed, the key might vanish.

        You should ALWAYS use a try: ... except KeyError: ... block.

        >>> d = LRUCacheDict(max_size=3, expiration=1)
        >>> d['foo'] = 'bar'
        >>> d['foo']
        'bar'
        >>> import time
        >>> if d.has_key('foo'):
        ...    time.sleep(2) #Oops, the key 'foo' is gone!
        ...    d['foo']
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        """
        return self._redis.exists(key)

    @_lock_decorator
    def __setitem__(self, key, value):
        self._redis.set(key, value, self.expiration)
        self.cleanup()

    @_lock_decorator
    def __getitem__(self, key):
        return self._redis.get(key)

    @_lock_decorator
    def __delete__(self, key):
        self._redis.delete([key])

    @_lock_decorator
    def cleanup(self):
        keys = self._redis.keys()
        a_range = self.size() - self.max_size
        if a_range > 0:
            self._redis.delete(keys[0:a_range])


if __name__ == "__main__":
    __store_type = STORE_TYPE.REDIS
    __file_config = ''


    class TestCache:
        # @staticmethod
        @lru_cache_function()
        def test(self, x):
            print("TestCache::test param %s" % x)
            return x + 1


    @lru_cache_function()
    def some_expensive_method(x):
        print("Calling some_expensive_method(" + str(x) + ")")
        return x + 200


    @lru_cache_function()
    def obj_some_expensive_method(x):
        print("Calling some_expensive_method(" + str(x) + ")")
        return {"title": "data", "value": x}


    # This will print "Calling f(3)", will return 3
    print('cache value', some_expensive_method(3))
    # This will not print anything, but will return 3 (unless 15 minutes
    # have passed between the first and second function call).
    print('get cache value', some_expensive_method(3))

    # cache new value
    print('cache new value', some_expensive_method(4))
    # get cache new value
    print('get cache new value', some_expensive_method(4))

    # get cache old value
    print('get cache old value', some_expensive_method(3))

    d = LRUCacheDict(max_size=3, expiration=3)
    d['foo'] = 'bar'
    print(d['foo'])  # prints "bar"

    # 4 seconds > 3 second cache expiry of d
    time.sleep(4)
    # KeyError
    try:
        print(d['foo'])
    except KeyError:
        print("not have foo")

    obj = obj_some_expensive_method(3)
    print(obj)

    obj['title'] = "new value"

    print(obj_some_expensive_method(3))

    tc = TestCache()
    tt = tc.test(1)
    tt += tc.test(2)
    tt += tc.test(2)
    print(tt)
