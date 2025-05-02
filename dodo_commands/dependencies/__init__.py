import importlib
import os
import sys
from types import ModuleType


class Switcher:
    def __init__(self):
        self.is_private = False
        self.public_sys_modules = {}
        self.private_sys_modules = {}
        self.package_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "packages"
        )
        self.built_in = {}
        for x in sys.builtin_module_names:
            self.built_in[x] = True
            if x.startswith("_"):
                self.built_in[x[1:]] = True

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
        self.is_private = True

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
        self.is_private = False


switcher = Switcher()


class private_sys_modules:
    def __enter__(self):
        self.is_switching = not switcher.is_private
        if self.is_switching:
            switcher.switch_to_private()
        return self

    def __exit__(self, *exc):
        if self.is_switching and switcher.is_private:
            switcher.switch_to_public()
        return False


def get_dependency(path):
    if path in switcher.private_sys_modules:
        return switcher.private_sys_modules[path]

    with private_sys_modules():
        return importlib.import_module(path)


class LocalModule(ModuleType):
    """The module-hack that allows us to use ``from dependencies.get import some_module``"""

    __all__ = ()  # to make help() happy
    __package__ = __name__

    def __getattr__(self, name):
        name_ext = (
            "ruamel.yaml"
            if name == "yaml"
            else "funcy.py2" if name == "funcy" else name
        )
        return get_dependency(name_ext)

    __path__ = []  # type: List[str]
    __file__ = __file__


get = LocalModule(__name__ + ".get", LocalModule.__doc__)
sys.modules[get.__name__] = get


def yaml_round_trip_load(text):
    with private_sys_modules():
        yaml = get_dependency("ruamel.yaml")
        return yaml.round_trip_load(text)


def yaml_round_trip_dump(text):
    with private_sys_modules():
        yaml = get_dependency("ruamel.yaml")
        return yaml.round_trip_dump(text)
