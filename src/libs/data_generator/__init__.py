import random
import string
import time
from datetime import datetime, timedelta, timezone

import names


class DataGenerator:
    @staticmethod
    def get_name(filename):
        return names.get_name(filename)

    @staticmethod
    def get_first_name(gender=None):
        return names.get_full_name(gender)

    @staticmethod
    def get_last_name():
        return names.get_last_name()

    @staticmethod
    def get_full_name(gender=None):
        return names.get_first_name(gender)

    @staticmethod
    def get_id(size=6, chars=string.ascii_uppercase + string.digits) -> str:
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_chars(size=6, chars=string.ascii_uppercase) -> str:
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_ipv4():
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))

    @staticmethod
    def get_local_ipv4():
        suffix = '.'.join(str(random.randint(0, 255)) for _ in range(2))
        return "192.168." + suffix

    @staticmethod
    def get_port():
        return random.randint(1, 65535)

    @staticmethod
    def get_ipv6():
        return ':'.join(
            ''.join(random.choice(string.hexdigits).lower() for _ in range(4))
            for _ in range(8)
        )

    @staticmethod
    def get_datetime(min_year=1900, max_year=datetime.now().year) -> datetime:
        # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * random.random()

    @staticmethod
    def convert_timestamp(dt):
        epoch = dt - timedelta(days=1900)
        td = dt - epoch
        return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6

    @staticmethod
    def get_timestamp():
        start = DataGenerator.convert_timestamp(datetime.now(tz=timezone.utc))
        stop = time.time()
        return random.uniform(start, stop)

    @staticmethod
    def get_protocol():
        proto_names = ["UDP", "HTTP", "HTTPS", 'TCP/IP', 'DHCP', 'SSH', 'SMTP', 'POP3', 'FTP', 'WAP', 'MIME', 'RDP']
        return random.choice(proto_names)

    @staticmethod
    def get_sentence():
        s_nouns = ["A dude", "My mom", "The king", "Some guy", "A cat with rabies", "A sloth", "Your homie",
                   "This cool guy my gardener met yesterday", "Superman"]
        p_nouns = ["These dudes", "Both of my moms", "All the kings of the world", "Some guys",
                   "All of a cattery's cats",
                   "The multitude of sloths living under your bed", "Your homies",
                   "Like, these, like, all these people",
                   "Supermen"]
        s_verbs = ["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on",
                   "retards", "meows on", "flees from", "tries to automate", "explodes"]
        infinitives = ["to make a pie.", "for no apparent reason.", "because the sky is green.", "for a disease.",
                       "to be able to make toast explode.", "to know more about archeology."]
        terms = [random.choice(s_nouns), random.choice(s_verbs), random.choice(
            s_nouns).lower() or random.choice(
            p_nouns).lower(), random.choice(infinitives)]
        return ' '.join(terms)

    @staticmethod
    def get_integer(start: int, stop: int) -> int:
        return random.randint(start, stop)

    @staticmethod
    def get_float(start: int, stop: int, ndigits: int = 4) -> float:
        return round(random.uniform(start, stop), ndigits)

    @staticmethod
    def get_latitude() -> float:
        return DataGenerator.get_float(-90, 90)

    @staticmethod
    def get_longitude() -> float:
        return DataGenerator.get_float(-180, 180)


# --------------------------- TEST ---------------------------
if __name__ == '__main__':
    print("get_full_name:", DataGenerator.get_full_name())
    print('get_full_name(male):', DataGenerator.get_full_name(gender='male'))
    print('get_first_name:', DataGenerator.get_first_name())
    print('get_first_name(female):', DataGenerator.get_first_name(gender='female'))
    print('get_last_name:', DataGenerator.get_last_name())
    print('get_timestamp:', DataGenerator.get_timestamp())
    print('get_ipv4:', DataGenerator.get_ipv4())
    print('get_ipv6:', DataGenerator.get_ipv6())
    print('get_local_ipv4:', DataGenerator.get_local_ipv4())
    print('get_datetime:', DataGenerator.get_datetime())
    print('get_protocol:', DataGenerator.get_protocol())
    print('get_sentence:', DataGenerator.get_sentence())
    print('get_integer:', DataGenerator.get_integer(0, 10))
    print('get_float:', DataGenerator.get_float(-180, 180))
