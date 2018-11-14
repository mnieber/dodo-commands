from dodo_commands.framework.util import classproperty, query_yes_no
from importlib import import_module
import argcomplete
import argparse
import fnmatch
import os
import sys
from dodo_commands.framework.config import (ConfigLoader, look_up_key,
                                            CommandPath)
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from plumbum import FG, ProcessExecutionError, local


def _ask_to_continue(args, cwd, is_echo, is_confirm):
    """Ask the user whether to continue with executing func."""

    def to_str():
        return args.to_str(slash=args.children)

    if is_echo:
        print(to_str())
        return False

    if is_confirm:
        print("(%s) %s" % (cwd, to_str()))
        if not query_yes_no("continue?"):
            return False
        else:
            print("")

    return True


class DecoratorScope:
    def __init__(self, decorator_name):
        self.decorators = Dodo.config['ROOT']['decorators'].setdefault(
            decorator_name, [])

    def __enter__(self):  # noqa
        self.decorators.append(Dodo.command_name)

    def __exit__(self, type, value, traceback):  # noqa
        self.decorators.remove(Dodo.command_name)


class Dodo:
    command_name = None
    safe = True
    args = argparse.Namespace()

    _config = None

    @classproperty
    def config(cls):  # noqa
        if cls._config is None:
            cls._config = ConfigLoader().load()
        return cls._config

    @classmethod
    def create_get_config(cls, local_vars):
        """
        Returns a get_config function that interpolates local_vars.
        For example:

        gc = Dodo.create_get_config(dict(user='sam'))
        tmp_dir = gc('/USERS/{user}/tmp_dir', default='/tmp')
        """

        def get_config(key, default=None):
            return cls.get_config(key.format(**local_vars), default)

        return get_config

    @classmethod
    def get_config(cls, key, default_value="__not_set_234234__"):  # noqa
        return look_up_key(cls.config, key, default_value)

    @classmethod
    def is_main(cls, name, safe=None):
        if safe is not None:
            cls.safe = safe
        return name in ('__main__', cls.package_path + '.' + cls.command_name)

    @classmethod
    def _get_decorators(cls):
        return [
            cls._load_decorator(name, directory)
            for name, directory in cls.all_decorators().items()
            if cls._uses_decorator(name)
        ]

    @classmethod
    def _uses_decorator(cls, decorator_name):
        patterns = (cls.config.get('ROOT', {}).get('decorators', {}).get(
            decorator_name, []))
        command_name = cls.command_name
        approved = [
            pattern for pattern in patterns if not pattern.startswith("!")
            and fnmatch.filter([command_name], pattern)
        ]
        rejected = [
            pattern for pattern in patterns if pattern.startswith("!")
            and fnmatch.filter([command_name], pattern[1:])
        ]
        return len(approved) and not len(rejected)

    @classmethod
    def _load_decorator(cls, name, directory):
        """Load and return decorator class in module with given name."""
        return import_module(directory + "." + name).Decorator()

    @classmethod
    def all_decorators(cls):
        """Returns a mapping from decorator name to its directory."""
        command_path = CommandPath(cls.config)
        command_path.extend_sys_path()
        result = {}
        for item in command_path.items:
            try:
                module_path = os.path.basename(item) + ".decorators"
                module = import_module(module_path)
                for decorator in os.listdir(module.__path__[0]):
                    name, ext = os.path.splitext(decorator)
                    if ext == '.py' and name != '__init__':
                        result[name] = module_path
            except ImportError:
                continue
        return result

    @classmethod
    def parse_args(cls, parser):
        if not cls.command_name:
            argcomplete.autocomplete(parser)
            return parser.parse_args(sys.argv)

        parser.add_argument(
            '--traceback', action='store_true', help=argparse.SUPPRESS)

        parser.add_argument(
            '--confirm',
            action='store_true',
            help="Confirm each performed action before its execution")

        parser.add_argument(
            '--echo',
            action='store_true',
            help="Print all commands instead of running them")

        for decorator in cls._get_decorators():
            decorator.add_arguments(parser)

        argcomplete.autocomplete(parser)
        parser.prog = "%s %s" % (os.path.basename(sys.argv[0]), sys.argv[1])
        cls.args = parser.parse_args(sys.argv[2:])

        if cls.args.echo and not cls.safe:
            raise CommandError(
                "The --echo option is not supported for unsafe commands.\n" +
                "Since this command is marked as unsafe, some operations will "
                + "be performed directly, instead of echoed to the console. " +
                "Use --confirm if you wish to execute with visual feedback. ")

        if cls.args.confirm and not cls.safe:
            if not query_yes_no(
                    "Since this command is marked as unsafe, some operations will "
                    +
                    "be performed without asking for confirmation. Continue?",
                    default="no"):
                return

        return cls.args

    @classmethod
    def run(cls, args, cwd=None, quiet=False, capture=False):
        if not hasattr(cls.args, 'echo'):
            raise CommandError('Dodo.run was called without first calling '
                               'Dodo.parse_args.')
        root_node = ArgsTreeNode('original_args', args=args)
        for decorator in cls._get_decorators():
            root_node, cwd = decorator.modify_args(root_node, cwd)

        if not _ask_to_continue(root_node, cwd or local.cwd, cls.args.echo,
                                cls.args.confirm):
            return False

        if cwd and not os.path.exists(cwd):
            raise CommandError("Directory not found: %s" % cwd)

        with local.cwd(cwd or local.cwd):
            flat_args = root_node.flatten()
            func = local[flat_args[0]][flat_args[1:]]
            variable_map = cls.get_config('/ENVIRONMENT/variable_map', {})
            with local.env(**variable_map):
                if capture:
                    return func()
                try:
                    func & FG
                    return True
                except ProcessExecutionError:
                    if not quiet:
                        print(
                            "\nDodo Commands error while running this command:"
                        )
                        print("\n\n%s" % func)
                    return False

    # add alias for the legacy 'runcmd' method
    runcmd = run

    @classmethod
    def decorator(cls, decorator_name):
        return DecoratorScope(decorator_name)
