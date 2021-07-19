from mocobot.framework.runtime import Runtime as FrameworkRuntime
from mocobot.application.injector import Injector
from mocobot.application.application import Application
from typing import List


class Runtime(FrameworkRuntime):

    def run(self, args: List[str]):
        self._run(Injector, Application, "test_app", config_path="../cihatbot.local.cfg")
