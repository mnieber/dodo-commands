import argparse
import os
import sys

from dodo_commands.dependencies.get import argcomplete, plumbum
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_arg import add_config_args
from dodo_commands.framework.config_key import Key, KeyNotFound
from dodo_commands.framework.container.container import Container
from dodo_commands.framework.decorator_utils import get_decorators
from dodo_commands.framework.util import classproperty


class Dodo:
    safe = True
    parser = argparse.ArgumentParser()

    _args = None
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

    @classproperty
    def args(cls):  # noqa
        if cls._args is None:
            cls.parse_args(cls.parser)
        return cls._args

    @classproperty
    def command_name(cls):  # noqa
        return cls.get_container().command_line.command_name

    @classmethod
    def get(cls, key="", default_value="__not_set_234234__"):  # noqa
        try:
            return Key(cls.get_container().config.config, key).get()
        except KeyNotFound:
            if default_value == "__not_set_234234__":
                raise
            return default_value

    @classmethod
    def is_main(cls, name, safe=None):
        if safe is not None:
            cls.safe = safe

        for decorator in get_decorators(
            cls.command_name,
            cls.get(),
            decorators_from_input_args=(
                cls.get_container().command_line.decorators_from_input_args
            ),
        ):
            if hasattr(decorator, "install"):
                decorator.install()

        if name == "__main__":
            return True

        commands = cls.get_container().commands
        command_map_item = commands.command_map.get(cls.command_name, None)
        if not command_map_item:
            return False

        script_path = command_map_item.package_path + "." + cls.command_name
        return name == script_path

    @classmethod
    def parse_args(cls, parser=None, config_args=None, strict=True):
        parser = parser or cls.parser

        parser.add_argument("--traceback", action="store_true", help=argparse.SUPPRESS)

        add_config_args(parser, cls.get(), config_args)

        for decorator in get_decorators(
            cls.command_name,
            cls.get(),
            decorators_from_input_args=(
                cls.get_container().command_line.decorators_from_input_args
            ),
        ):
            decorator.add_arguments(parser)

        args = cls.get_container().command_line.input_args
        parser.prog = os.path.basename(args[0])
        if len(args) > 1:
            parser.prog += " %s" % args[1]

        if cls.get_container().command_line.is_help:
            parser.print_help()
            sys.exit(0)

        argcomplete.autocomplete(parser)
        if strict:
            more_args = None
            cls._args = parser.parse_args(args[2:])
        else:
            cls._args, more_args = parser.parse_known_args(args[2:])

        if config_args:
            for config_arg in config_args:
                if config_arg.exists(cls.get()):
                    setattr(cls._args, config_arg.arg_name, config_arg.get(cls.get()))

        if strict:
            return cls._args
        else:
            return cls._args, more_args

    @classmethod
    def run(
        cls,
        args,
        cwd=None,
        quiet=False,
        capture=False,
    ):
        if cls.get_container().command_line.env_vars_from_input_args:
            for env_var in cls.get_container().command_line.env_vars_from_input_args:
                key, value = env_var.split("=")
                variable_map = (
                    Dodo.get()
                    .setdefault("ENVIRONMENT", {})
                    .setdefault("variable_map", {})
                )
                variable_map[key] = value

        cwd = cwd or cls.get_container().command_line.cwd
        args_tree_root_node = ArgsTreeNode("original_args", args=args)
        for decorator in get_decorators(
            cls.command_name,
            cls.get(),
            decorators_from_input_args=(
                cls.get_container().command_line.decorators_from_input_args
            ),
        ):
            args_tree_root_node, cwd = decorator.modify_args(
                cls._args, args_tree_root_node, cwd
            )
            if args_tree_root_node is None:
                return False

        if cwd and not os.path.exists(cwd):
            raise CommandError("Directory not found: %s" % cwd)

        with plumbum.local.cwd(cwd or plumbum.local.cwd):
            flat_args = args_tree_root_node.flatten()
            func = plumbum.local[flat_args[0]][flat_args[1:]]

            variable_map = cls.get("/ENVIRONMENT/variable_map", {})
            with plumbum.local.env(**variable_map):
                if capture:
                    return func()
                try:
                    func & plumbum.FG
                    return True
                except plumbum.ProcessExecutionError:
                    if not quiet:
                        print("\nDodo Commands error while running this command:")
                        print("\n\n%s" % func)
                    return False

    # add alias for the legacy 'runcmd' method
    runcmd = run
    get_config = get
