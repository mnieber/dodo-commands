from dodo_commands.framework.util import query_yes_no
from importlib import import_module
import argcomplete
import argparse
import fnmatch
import os
import sys
from dodo_commands.framework.config import (ConfigLoader, get_command_path)
from dodo_commands.framework.config_expander import Key, KeyNotFound
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from plumbum import FG, ProcessExecutionError, local


def _ask_confirmation(args, cwd, is_echo, is_confirm):
    """Ask the user whether to continue with executing func."""

    def to_str():
        return args.to_str(slash=args.children)

    if is_echo:
        print(to_str())
        return False

    if is_confirm:
        print("(%s) %s" % (cwd, to_str()))
        if not query_yes_no("confirm?"):
            return False
        else:
            print("")

    return True


class DecoratorScope:
    def __init__(self, decorator_name):
        self.decorators = Dodo.get_config('/ROOT').setdefault(
            'decorators', {}).setdefault(decorator_name, [])

    def __enter__(self):  # noqa
        self.decorators.append(Dodo.command_name)

    def __exit__(self, type, value, traceback):  # noqa
        self.decorators.remove(Dodo.command_name)


class ConfigArg:
    def __init__(self, config_key, *args, **kwargs):
        self.config_key = config_key
        self.args = args
        self.kwargs = kwargs

    @property
    def arg_name(self):
        return self.args[0].strip('-').replace('-', '_')

    @property
    def xpath(self):
        return [x for x in self.config_key.split('/') if x]


class Dodo:
    package_path = None
    command_name = None
    safe = True

    _args = argparse.Namespace()
    _config = None

    @classmethod
    def get_config(cls, key='', default_value="__not_set_234234__"):  # noqa
        if cls._config is None:
            cls._config = ConfigLoader().load()

        try:
            xpath = [k for k in key.split("/") if k]
            return Key(cls._config, xpath).get()
        except KeyNotFound:
            if default_value == "__not_set_234234__":
                raise
            return default_value

    @classmethod
    def is_main(cls, name, safe=None):
        if safe is not None:
            cls.safe = safe

        if name == '__main__':
            import __main__ as main
            cls.command_name = os.path.basename(main.__file__)
            return True

        return (cls.command_name and cls.package_path
                and name == cls.package_path + '.' + cls.command_name)

    @classmethod
    def _get_decorators(cls):
        return [
            cls._load_decorator(name, directory)
            for name, directory in cls._all_decorators().items()
            if cls._uses_decorator(name)
        ]

    @classmethod
    def _uses_decorator(cls, decorator_name):
        patterns = (cls.get_config().get('ROOT',
                                         {}).get('decorators',
                                                 {}).get(decorator_name, []))
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
    def _all_decorators(cls):
        """Returns a mapping from decorator name to its directory."""
        command_path = get_command_path(cls.get_config())
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
    def _add_config_args(cls, parser, config_args=None):
        show_help = '--help' in sys.argv

        for config_arg in (config_args or []):
            key = Key(cls.get_config(), config_arg.xpath)
            key_exists = key.exists()

            if show_help or not key_exists:
                kwargs = dict(config_arg.kwargs)
                help_text = kwargs.get('help') or ''
                sep = '. ' if help_text else ''
                if key_exists:
                    value = str(key.get())
                    formatted_value = value[:50] + (value[50:] and '...')
                    extra_help = ('Read from config: %s = %s.' %
                                  (config_arg.config_key, formatted_value))
                else:
                    extra_help = ('Configuration key is %s' %
                                  config_arg.config_key)

                kwargs['help'] = help_text + sep + extra_help
                parser.add_argument(*config_arg.args, **kwargs)

    @classmethod
    def _is_confirm(cls):
        return getattr(cls._args, 'confirm', False) or os.environ.get(
            '__DODO_UNIVERSAL_CONFIRM__', None) == '1'

    @classmethod
    def _is_echo(cls):
        return getattr(cls._args, 'echo', False)

    @classmethod
    def parse_args(cls, parser, config_args=None):
        parser.add_argument('--traceback',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument(
            '-c',
            '--confirm',
            action='count',
            help="Confirm each performed action before its execution." +
            " Use twice (e.g. dodo foo -cc) to indicate that also nested calls must be confirmed."
        )

        parser.add_argument('-e',
                            '--echo',
                            action='store_true',
                            help="Print all commands instead of running them")

        # The --layer option is handled by the argument parser in ConfigLoader.
        # We need to add it to this parser as well, otherwise it will complain.
        # Yes, quite hacky...
        parser.add_argument('--layer', action='append', help=argparse.SUPPRESS)

        for decorator in cls._get_decorators():
            decorator.add_arguments(parser)

        cls._add_config_args(parser, config_args)
        argcomplete.autocomplete(parser)
        if os.path.splitext(sys.argv[0])[1].lower() == '.py':
            parser.prog = sys.argv[0]
            first_arg_index = 1
        else:
            first_arg_index = 2
            parser.prog = "%s %s" % (os.path.basename(
                sys.argv[0]), sys.argv[1])
        cls._args = parser.parse_args(sys.argv[first_arg_index:])

        if cls._args.confirm and cls._args.confirm > 1:
            local.env['__DODO_UNIVERSAL_CONFIRM__'] = '1'

        if config_args:
            for config_arg in config_args:
                key = Key(cls.get_config(), config_arg.xpath)
                if key.exists():
                    setattr(cls._args, config_arg.arg_name, key.get())

        if cls._args.echo and not cls.safe:
            raise CommandError(
                "The --echo option is not supported for unsafe commands.\n" +
                "Since this command is marked as unsafe, some operations will "
                + "be performed directly, instead of echoed to the console. " +
                "Use --confirm if you wish to execute with visual feedback. ")

        if cls._is_confirm() and not cls.safe:
            if not query_yes_no(
                    "Since this command is marked as unsafe, some operations will "
                    +
                    "be performed without asking for confirmation. Continue?",
                    default="no"):
                sys.exit(1)

        return cls._args

    @classmethod
    def run(cls, args, cwd=None, quiet=False, capture=False):
        root_node = ArgsTreeNode('original_args', args=args)
        for decorator in cls._get_decorators():
            root_node, cwd = decorator.modify_args(cls._args, root_node, cwd)

        if not _ask_confirmation(root_node, cwd or local.cwd, cls._is_echo(),
                                 cls._is_confirm()):
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
