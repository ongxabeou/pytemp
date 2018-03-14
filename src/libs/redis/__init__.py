import ast

import redis
import configparser


class REDIS_MODE:
    HOST = 'host'
    PORT = 'port'
    EXPIRED_TIME_FOR_KEY = 'expired_time_for_key'
    EXPIRED_TIME_FOR_GROUP = 'expired_time_for_group'


class RedisStorage:
    def __init__(self, config_file_name):
        self._sections = {}
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name, 'utf-8')
        self.host = self._get_section_map(REDIS_MODE.__name__)[REDIS_MODE.HOST]
        self.port = self._get_section_map(REDIS_MODE.__name__)[REDIS_MODE.PORT]
        self.expired_time_for_key = int(self._get_section_map(REDIS_MODE.__name__)[REDIS_MODE.EXPIRED_TIME_FOR_KEY])
        self.expired_time_for_group = int(self._get_section_map(REDIS_MODE.__name__)[REDIS_MODE.EXPIRED_TIME_FOR_GROUP])
        self._redis = redis.Redis(host=self.host, port=self.port, db=0)

    def _get_section_map(self, section):
        if section in self._sections:
            return self._sections[section]

        local_dic = {}
        options = self.config.options(section)
        for option in options:
            try:
                local_dic[option] = self.config.get(section, option)
                if local_dic[option] == -1:
                    print("skip: %s" % option)
            except Exception as ex:
                print("get section of SystemConfig %s option %s have error:%s!" % (section, option, ex))
                local_dic[option] = None
        self._sections[section] = local_dic
        return local_dic

    def get_instance(self):
        return self._redis

    def get(self, key):
        return self._redis.get(key)

    def set(self, key, value, group_id=None):
        if group_id:
            self.append_key_to_group(group_id, key)
        return self._redis.set(key, value, self.expired_time_for_key)

    def append_key_to_group(self, group_id, key):
        keys = self.get_keys_from_group(group_id)
        keys.append(key)
        return self._redis.set(group_id, keys, self.expired_time_for_group)

    def get_keys_from_group(self, group_id):
        keys = []
        value = self._redis.get(group_id)
        if value is not None:
            # chuyển giá trị string về mảng
            keys = ast.literal_eval(str(value.decode("utf-8")))
        return keys

    def delete(self, key, group_id=None):
        if group_id:
            keys = self.get_keys_from_group(group_id)
            try:
                keys.remove(key)
                self._redis.set(group_id, keys, self.expired_time_for_group)
            except ValueError:
                pass
        return self._redis.hdel("key", key)

    def delete_all_key_by_groups(self, group_ids):
        print('delete_all_key_by_groups: %s' % str(group_ids))
        if group_ids is not None and (isinstance(group_ids, list) or isinstance(group_ids, set)):
            for group_id in group_ids:
                keys = self.get_keys_from_group(group_id)
                self._redis.hdel("Group", group_id)
                for key in keys:
                    print('delete_all_key_by_groups: delete key: %s' % key)
                    self._redis.hdel("Key", key)
            return True
        else:
            print('delete_all_key_by_groups: group_ids must be not none and is list or set')
            return False
