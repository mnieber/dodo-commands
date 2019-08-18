import argcomplete
import argparse
import os
import sys

from plumbum import FG, ProcessExecutionError, local

from dodo_commands.framework.config import ConfigLoader
from dodo_commands.framework.config_layers import get_layers
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.config_arg import add_config_args
from dodo_commands.framework.decorator_utils import get_decorators
from dodo_commands.framework.config_expander import Key, KeyNotFound
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError


class Dodo:
    script_path = None
    command_name = None
    safe = True

    _command_line_args = argparse.Namespace()
    _config = None

    @classmethod
    def _extra_layers(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--layer', action='append', help=argparse.SUPPRESS)
        args, _ = parser.parse_known_args(
            [x for x in sys.argv if x not in ('--help', '-h')])
        return args.layer or []

    @classmethod
    def get_config(cls, key='', default_value="__not_set_234234__"):  # noqa
        if cls._config is None:
            base_config = ConfigIO().load()
            layer_filenames = get_layers(base_config, extra_layers=cls._extra_layers())
            cls._config = ConfigLoader().load(layer_filenames, base_config=base_config)

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

        if name not in ('__main__', cls.script_path):
            return False

        main_file_basename = os.path.basename(sys.modules[name].__file__)
        cls.command_name = os.path.splitext(main_file_basename)[0]
        return True

    @classmethod
    def parse_args(cls, parser, config_args=None):
        parser.add_argument('--traceback',
                            action='store_true',
                            help=argparse.SUPPRESS)

        # The --layer option is handled by the argument parser in cls._extra_layers.
        # We need to add it to this parser as well, otherwise it will complain.
        parser.add_argument('--layer', action='append', help=argparse.SUPPRESS)

        for decorator in get_decorators(cls.command_name, cls.get_config()):
            decorator.add_arguments(parser)

        add_config_args(parser, cls.get_config(), config_args)
        argcomplete.autocomplete(parser)
        if os.path.splitext(sys.argv[0])[1].lower() == '.py' or len(sys.argv) == 1:
            parser.prog = sys.argv[0]
            first_arg_index = 1
        else:
            first_arg_index = 2
            parser.prog = "%s %s" % (os.path.basename(sys.argv[0]), sys.argv[1])

        cls._command_line_args = parser.parse_args(sys.argv[first_arg_index:])

        if config_args:
            for config_arg in config_args:
                key = Key(cls.get_config(), config_arg.xpath)
                if key.exists():
                    setattr(cls._command_line_args, config_arg.arg_name, key.get())

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
