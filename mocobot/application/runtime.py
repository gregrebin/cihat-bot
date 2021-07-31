from mocobot.framework.runtime import Runtime as FrameworkRuntime
from mocobot.application.injector import Injector
from mocobot.application.application import Application
from configparser import ConfigParser
from typing import List


class Runtime(FrameworkRuntime):

    async def start(self, args: List[str]):
        configparser = ConfigParser()
        configparser.read("../cihatbot.local.cfg")
        injector = Injector(configparser)
        application = injector.inject(Application, "test_app")
        await self.run(application)
