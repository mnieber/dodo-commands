"""Package default_commands."""
import os

from dodo_commands.framework import (BaseCommand, CommandPath)
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config import load_dodo_config

from importlib import import_module
from plumbum import FG, ProcessExecutionError, local
from dodo_commands.framework.util import query_yes_no


class DodoCommand(BaseCommand):  # noqa
    safe = True
    decorators = []
    _loaded_decorators = None

    @staticmethod
    def _load_decorator(name, config):
        """Load and return decorator class in module with given name."""
        command_path = CommandPath(config)
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

        for decorator in self._get_decorators(load_dodo_config()):
            decorator.add_arguments(self, parser)

        self.add_arguments_imp(parser)

    def _get_decorators(self, config):
        if self._loaded_decorators is None:
            self._loaded_decorators = [
                self._load_decorator(d, config) for d in self.decorators
                if d is not None
            ]

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

        if echo and not self.safe:
            raise CommandError(
                "The --echo option is not supported for unsafe commands.\n" +
                "Since this command is marked as unsafe, some operations will " +
                "be performed directly, instead of echoed to the console. " +
                "Use --confirm if you wish to execute with visual feedback. "
            )

        if confirm and not self.safe:
            if not query_yes_no(
                "Since this command is marked as unsafe, some operations will " +
                "be performed without asking for confirmation. Continue?",
                default="no"
            ):
                return

        for decorator in self._get_decorators(self.config):
            decorator.handle(self, **kwargs)
        self.handle_imp(**kwargs)

    def handle_imp(self, **kwargs):  # noqa
        raise CommandError("Not implemented")

    def runcmd(self, args, cwd=None):
        for decorator in self._get_decorators(self.config):
            args, cwd = decorator.modify_args(self, args, cwd)

        func = local[args[0]][args[1:]]
        if self.opt_echo:
            print(func)
            return False

        if self.opt_confirm:
            print("(%s) %s" % (cwd or local.cwd, func))
            if not query_yes_no("continue?"):
                return False
            print()

        if cwd and not os.path.exists(cwd):
            raise CommandError("Directory not found: %s" % cwd)

        with local.cwd(cwd or local.cwd):
            try:
                variable_map = self.get_config('/ENVIRONMENT/variable_map', {})
                with local.env(**variable_map):
                    func & FG
                return True
            except ProcessExecutionError:
                print("\nDodo Commands error while running this command:\n\n%s" % func)
                return False
