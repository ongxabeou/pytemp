#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/04/28
"""


class Singleton(object):
    """Singleton decorator."""

    def __init__(self, cls):
        self.__dict__['cls'] = cls

    instances = {}

    def __call__(self):
        if self.cls not in self.instances:
            self.instances[self.cls] = self.cls()
        return self.instances[self.cls]

    def __getattr__(self, attr):
        return getattr(self.__dict__['cls'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['cls'], attr, value)


# ------------------Test------------------------
if __name__ == '__main__':
    @Singleton
    class bar(object):
        def __init__(self):
            self.val = None


    @Singleton
    class poo(object):
        def __init__(self):
            self.val = None

        def activated(self, acc_id):
            self.val = acc_id


    x = bar()
    x.val = 'sausage'
    print(x, x.val)
    y = bar()
    y.val = 'eggs'
    print(y, y.val)
    z = bar()
    z.val = 'spam'
    print(z, z.val)
    print(x is y is z)

    x = poo()
    x.val = 'sausage'
    print(x, x.val)
    y = poo()
    y.val = 'eggs'
    print(y, y.val)

    x = poo()
    x.activated(123)
    print(x.val)
