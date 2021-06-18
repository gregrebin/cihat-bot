from mocobot.runtime import Runtime
from mocobot.application.injector import Injector


if __name__ == '__main__':
    Runtime(Injector, "mocobot.local.cfg").run("test_app")

