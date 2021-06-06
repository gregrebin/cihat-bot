from cihatbot.framework.injector import Injector as ModuleInjector, Type, ModuleType
from cihatbot.application.application import Application


class Injector(ModuleInjector):

    def test(self):
        app = Application({})
        return app

    def inject(self, module_type: Type[ModuleType], name: str) -> ModuleType:
        return super().inject(module_type, name)



