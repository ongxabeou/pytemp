class Foo(object):
    def __init__(self, other=None):
        # make a circular reference
        self.link = other
        if other is not None:
            other.link = self

    def my_func(self):
        print("deling", self)


def created_foo():
    return Foo(Foo())


if __name__ == '__main__':
    # import gc

    # gc.disable()
    f = Foo(Foo())
    func = f.my_func
    my_tuple = (1, "hello", Foo())
    my_dict = {
        'int': 1,
        'string': 'hellow',
        'object': Foo()
    }
    print(func)
    print("before")
    del func  # nothing gets deleted here
    try:
        print(func)
    except Exception as e:
        print(e)

    del my_tuple  # nothing gets deleted here
    try:
        print(my_tuple)
    except Exception as e:
        print(e)

    del my_dict  # nothing gets deleted here
    try:
        print(my_dict)
    except Exception as e:
        print(e)
    print("after")
    # created_foo()
    # gc.collect()
    f.my_func()
    # print(gc.garbage)  # The GC knows the two Foos are garbage, but won't delete
    #  them because they have a __del__ method
    # print("after gc")
    # break up the cycle and delete the reference from gc.garbage [ phá vỡ chu trình và xóa tham chiếu khỏi gc.garbage]
    # if len(gc.garbage) > 0:
    #     del gc.garbage[0].link, gc.garbage[:]
    # print("done")
