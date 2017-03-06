"""Package default_commands."""

from dodo_commands.framework import (
    BaseCommand, CommandPath, get_project_dir
)
from dodo_commands.framework.command_error import CommandError

from importlib import import_module
from plumbum import FG, ProcessExecutionError, local
from dodo_commands.framework.util import query_yes_no


class DodoCommand(BaseCommand):  # noqa
    decorators = []
    _loaded_decorators = None

    @staticmethod
    def _load_decorator(name):
        """Load and return decorator class in module with given name."""
        command_path = CommandPath(get_project_dir())
        command_path.extend_sys_path()
        for item in command_path.items:
            import_path = '%s.decorators.%s' % (
                item.module_path.replace("/", "."), name
            )
            try:
                module = import_module(import_path)
                return module.Decorator()
            except ImportError:
                continue
        return None

    def add_arguments(self, parser):
        """Entry point for subclassed commands to add custom arguments."""
        parser.add_argument(
            '--confirm',
            action='store_true',
            help="Confirm each performed action before its execution"
        )

        parser.add_argument(
            '--echo',
            action='store_true',
            help="Print all commands instead of running them"
        )

        for decorator in self._get_decorators():
            decorator.add_arguments(self, parser)

        self.add_arguments_imp(parser)

    def _get_decorators(self):
        if self._loaded_decorators is not None:
            return self._loaded_decorators

        self._loaded_decorators = list(filter(
            lambda x: x is not None,
            map(self._load_decorator, self.decorators)
        ))
        return self._loaded_decorators

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle(  # noqa
        self,
        confirm=False,
        echo=False,
        **kwargs
    ):
        self.opt_confirm = confirm
        self.opt_echo = echo

        for decorator in self._get_decorators():
            decorator.handle(self, **kwargs)
        self.handle_imp(**kwargs)

    def handle_imp(self, **kwargs):  # noqa
        raise CommandError("Not implemented")

    def runcmd(  # noqa
        self,
        args,
        cwd=None
    ):
        """
        Decorator to print function call details - parameters names and
        effective values.
        """
        for decorator in self._get_decorators():
            args, cwd = decorator.modify_args(self, args, cwd)

        func = local[args[0]][args[1:]]
        if self.opt_echo:
            print(func)
            return False

        with local.cwd(cwd or local.cwd):
            if self.opt_confirm:
                print("(%s) %s" % (local.cwd, func))
                if not query_yes_no("continue?"):
                    return False
                print()

            try:
                variable_map = self.get_config('/ENVIRONMENT/variable_map', {})
                with local.env(**variable_map):
                    func & FG
                return True
            except ProcessExecutionError:
                print("/nDodo Commands error while running this command:\n\n%s" % func)
                return False
