import importlib
import os
import sys
from types import ModuleType


class Switcher:
    def __init__(self):
        self.public_sys_modules = {}
        self.private_sys_modules = {}
        self.package_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "packages")
        self.built_in = {}
        for x in sys.builtin_module_names:
            self.built_in[x] = True

    def switch_to_private(self):
        # Move non-built-in modules to self.public_sys_modules
        for k, v in list(sys.modules.items()):
            if not self.built_in.get(k):
                self.public_sys_modules[k] = v
                del sys.modules[k]

        # Copy private modules to sys.modules
        for k, v in self.private_sys_modules.items():
            sys.modules[k] = v
        self.private_sys_modules.clear()

        sys.path = [self.package_path] + sys.path

    def switch_to_public(self):
        # Move non-built-in modules to self.private_sys_modules
        for k, v in list(sys.modules.items()):
            if not self.built_in.get(k):
                self.private_sys_modules[k] = v
                del sys.modules[k]

        # Copy public modules to sys.modules
        for k, v in self.public_sys_modules.items():
            sys.modules[k] = v
        self.public_sys_modules.clear()

        sys.path.remove(self.package_path)


switcher = Switcher()


def get_dependency(path):
    if path in switcher.private_sys_modules:
        return switcher.private_sys_modules[path]

    try:
        switcher.switch_to_private()
        return importlib.import_module(path)
    finally:
        switcher.switch_to_public()


class LocalModule(ModuleType):
    """The module-hack that allows us to use ``from dependencies.get import some_module``"""
    __all__ = ()  # to make help() happy
    __package__ = __name__

    def __getattr__(self, name):
        name_ext = ("ruamel.yaml" if name == "yaml" else
                    "funcy.py2" if name == "funcy" else name)
        return get_dependency(name_ext)

    __path__ = []  # type: List[str]
    __file__ = __file__


get = LocalModule(__name__ + ".get", LocalModule.__doc__)
sys.modules[get.__name__] = get
