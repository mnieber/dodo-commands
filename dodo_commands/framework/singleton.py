import argcomplete
import argparse
import os
import sys

from plumbum import FG, ProcessExecutionError, local

from dodo_commands.framework.config_arg import add_config_args
from dodo_commands.framework.decorator_utils import get_decorators
from dodo_commands.framework.config_expander import Key, KeyNotFound
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.util import classproperty
from dodo_commands.framework.container.container import Container


class Dodo:
    safe = True

    _command_line_args = argparse.Namespace()
    _container = None

    @classmethod
    def get_container(cls):
        if cls._container is None:
            cls._container = Container()
            cls._container.run_actions()

        return cls._container

    @classproperty
    def command_name(cls):  # noqa
        return cls.get_container().command_line.command_name

    @classmethod
    def get_config(cls, key='', default_value="__not_set_234234__"):  # noqa
        config = cls.get_container().config.config

        try:
            xpath = [k for k in key.split("/") if k]
            return Key(config, xpath).get()
        except KeyNotFound:
            if default_value == "__not_set_234234__":
                raise
            return default_value

    @classmethod
    def is_main(cls, name, safe=None):
        if safe is not None:
            cls.safe = safe

        if name == '__main__':
            return True

        commands = cls.get_container().commands
        command_map_item = commands.command_map.get(cls.command_name, None)
        if not command_map_item:
            return False

        script_path = command_map_item.package_path + '.' + cls.command_name
        return name == script_path

    @classmethod
    def parse_args(cls, parser, config_args=None):
        parser.add_argument('--traceback',
                            action='store_true',
                            help=argparse.SUPPRESS)

        add_config_args(parser, cls.get_config(), config_args)

        if cls.get_container().command_line.is_help:
            parser.print_help()
            sys.exit(0)

        for decorator in get_decorators(cls.command_name, cls.get_config()):
            decorator.add_arguments(parser)

        argcomplete.autocomplete(parser)

        args = cls.get_container().command_line.input_args
        parser.prog = os.path.basename(args[0])
        if len(args) > 1:
            parser.prog += " %s" % args[1]
        cls._command_line_args = parser.parse_args(args[2:])

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
