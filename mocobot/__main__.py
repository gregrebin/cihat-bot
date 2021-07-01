from mocobot.framework.runtime import Runtime
from mocobot.application.injector import Injector
from mocobot.application.application import Application


if __name__ == '__main__':
    Runtime(Injector, "mocobot.local.cfg").run(Application, "default_app")

