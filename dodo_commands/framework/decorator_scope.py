from dodo_commands.framework.singleton import Dodo


# Resp: add the current command_name
# to the list of commands decorated by decorator_name.
class DecoratorScope:
    def __init__(self, decorator_name, remove=False):
        self.decorators = (
            Dodo.get("/ROOT")
            .setdefault("decorators", {})
            .setdefault(decorator_name, [])
        )
        self.prefix = "!" if remove else ""

    def __enter__(self):  # noqa
        self.decorators.append(self.prefix + Dodo.command_name)

    def __exit__(self, type, value, traceback):  # noqa
        self.decorators.remove(self.prefix + Dodo.command_name)
