"""Pauses the execution."""
import time

from dodo_commands.framework.decorator_utils import uses_decorator


class Decorator:
    def is_used(self, config, command_name, decorator_name):
        return uses_decorator(config, command_name, decorator_name)

    def add_arguments(self, parser):  # override
        parser.add_argument(
            "--pause-ms", type=int, help="Pause in milliseconds before continuing"
        )

    def modify_args(self, command_line_args, args_tree_root_node, cwd):  # override
        if getattr(command_line_args, "pause_ms", 0):
            time.sleep(command_line_args.pause_ms / 1000)
        return args_tree_root_node, cwd
