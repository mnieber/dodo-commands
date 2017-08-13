"""Package default_commands."""
import fnmatch
import inspect
import os
from six.moves import configparser

from dodo_commands.framework import (BaseCommand, CommandPath)
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.args_tree import ArgsTreeNode

from importlib import import_module
from plumbum import FG, ProcessExecutionError, local
from dodo_commands.framework.util import query_yes_no


def _ask_to_continue(args, cwd, is_echo, is_confirm, pretty_print):
    """Ask the user whether to continue with executing func."""
    def to_str():
        if pretty_print:
            return args.to_str()
        return " ".join(args.flatten())

    if is_echo:
        print(to_str())
        return False

    if is_confirm:
        print("(%s) %s" % (cwd, to_str()))
        if not query_yes_no("continue?"):
            return False
        else:
            print()

    return True


class DodoCommand(BaseCommand):  # noqa
    safe = True
    _loaded_decorators = None

    def all_decorators(self):
        """Returns a mapping from decorator name to its directory."""
        command_path = CommandPath(self.config)
        command_path.extend_sys_path()
        result = {}
        for item in command_path.items:
            try:
                module_path = os.path.join(item.module_path, "decorators")
                module = import_module(module_path.replace("/", "."))
                for decorator in os.listdir(module.__path__[0]):
                    name, ext = os.path.splitext(decorator)
                    if ext == '.py' and name != '__init__':
                        result[name] = module_path
            except ImportError:
                continue
        return result

    @staticmethod
    def _load_decorator(name, directory):
        """Load and return decorator class in module with given name."""
        module = import_module(directory.replace("/", ".") + "." + name)
        return module.Decorator()

    def _command_name(self):
        script_filename = os.path.basename(inspect.getfile(self.__class__))
        return os.path.splitext(script_filename)[0]

    def _uses_decorator(self, decorator_name):
        patterns = (
            self.config.get('ROOT', {}).get('decorators', {}).get(decorator_name, [])
        )
        command_name = self._command_name()
        approved = [
            pattern for pattern in patterns if
            not pattern.startswith("!") and fnmatch.filter([command_name], pattern)
        ]
        rejected = [
            pattern for pattern in patterns if
            pattern.startswith("!") and fnmatch.filter([command_name], pattern[1:])
        ]
        return len(approved) and not len(rejected)

    def _get_decorators(self):
        if self._loaded_decorators is None:
            self._loaded_decorators = [
                self._load_decorator(name, directory)
                for name, directory in self.all_decorators().items()
                if self._uses_decorator(name)
            ]
        return self._loaded_decorators

    def _default_pretty_print(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.dodo_commands/config"))
        try:
            return config.get("DodoCommands", "pretty_print")
        except configparser.NoOptionError:
            return "true"

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

        parser.add_argument(
            '--pretty-print', '--pp',
            default=self._default_pretty_print(),
            choices=['yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0'],
            help="Use pretty printing for --echo and --confirm options"
        )

        for decorator in self._get_decorators():
            decorator.add_arguments(self, parser)

        self.add_arguments_imp(parser)

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle(  # noqa
        self,
        confirm=False,
        echo=False,
        pretty_print=True,
        **kwargs
    ):
        self.opt_confirm = confirm
        self.opt_echo = echo
        self.opt_pretty_print = pretty_print

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

        for decorator in self._get_decorators():
            decorator.handle(self, **kwargs)
        self.handle_imp(**kwargs)

    def handle_imp(self, **kwargs):  # noqa
        raise CommandError("Not implemented")

    def runcmd(self, args, cwd=None):
        root_node = ArgsTreeNode('original_args', args=args)
        for decorator in self._get_decorators():
            root_node, cwd = decorator.modify_args(self, root_node, cwd)

        if not _ask_to_continue(
            root_node,
            cwd,
            self.opt_echo,
            self.opt_confirm,
            self.opt_pretty_print in ('yes', 'true', 't', 'y', '1')
        ):
            return False

        if cwd and not os.path.exists(cwd):
            raise CommandError("Directory not found: %s" % cwd)

        with local.cwd(cwd or local.cwd):
            flat_args = root_node.flatten()
            func = local[flat_args[0]][flat_args[1:]]
            try:
                variable_map = self.get_config('/ENVIRONMENT/variable_map', {})
                with local.env(**variable_map):
                    func & FG
                return True
            except ProcessExecutionError:
                print("\nDodo Commands error while running this command:\n\n%s" % func)
                return False
