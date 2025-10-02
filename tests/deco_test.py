from unicex.utils import decorate_all_methods, catch_adapter_errors


@decorate_all_methods(catch_adapter_errors)
class Itest:
    pass


class Test(Itest):
    @staticmethod
    def t1(*args, **kwargs):
        raise Exception("test")


test = Test()
test.t1("1", "2", _3="3")
