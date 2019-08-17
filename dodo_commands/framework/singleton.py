import argcomplete
import argparse
import os
import sys
from dodo_commands.framework.config import ConfigLoader
from dodo_commands.framework.decorator_utils import get_decorators
from dodo_commands.framework.config_expander import Key, KeyNotFound
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from plumbum import FG, ProcessExecutionError, local


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


class Dodo:
    package_path = None
    command_name = None
    safe = True

    _command_line_args = argparse.Namespace()
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
    def parse_args(cls, parser, config_args=None):
        parser.add_argument('--traceback',
                            action='store_true',
                            help=argparse.SUPPRESS)

        # The --layer option is handled by the argument parser in ConfigLoader.
        # We need to add it to this parser as well, otherwise it will complain.
        # Yes, quite hacky...
        parser.add_argument('--layer', action='append', help=argparse.SUPPRESS)

        for decorator in get_decorators(cls.command_name, cls.get_config()):
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
        cls._command_line_args = parser.parse_args(sys.argv[first_arg_index:])

        if config_args:
            for config_arg in config_args:
                key = Key(cls.get_config(), config_arg.xpath)
                if key.exists():
                    setattr(cls._command_line_args, config_arg.arg_name,
                            key.get())

        return cls._command_line_args

    @classmethod
    def run(cls, args, cwd=None, quiet=False, capture=False):
        args_tree_root_node = ArgsTreeNode('original_args', args=args)
        for decorator in get_decorators(cls.command_name, cls.get_config()):
            args_tree_root_node, cwd = decorator.modify_args(
                cls._command_line_args, args_tree_root_node, cwd)
            if args_tree_root_node is None:
                return False

        if cwd and not os.path.exists(cwd):
            raise CommandError("Directory not found: %s" % cwd)

        with local.cwd(cwd or local.cwd):
            flat_args = args_tree_root_node.flatten()
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
