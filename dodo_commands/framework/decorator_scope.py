from dodo_commands.framework.singleton import Dodo


# Resp: add the current command_name
# to the list of commands decorated by decorator_name.
class DecoratorScope:
    def __init__(self, decorator_name):
        self.decorators = Dodo.get_config('/ROOT').setdefault(
            'decorators', {}).setdefault(decorator_name, [])

    def __enter__(self):  # noqa
        self.decorators.append(Dodo.command_name)

    def __exit__(self, type, value, traceback):  # noqa
        self.decorators.remove(Dodo.command_name)
