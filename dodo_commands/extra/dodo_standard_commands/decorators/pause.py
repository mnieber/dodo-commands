"""Pauses the execution."""
import time
from dodo_commands.framework import Dodo


class Decorator:  # noqa
    def add_arguments(self, parser):  # noqa
        parser.add_argument(
            '--pause-ms',
            type=int,
            help="Pause in milliseconds before continuing")

    def modify_args(self, root_node, cwd):  # noqa
        if Dodo.args.pause_ms:
            time.sleep(Dodo.args.pause_ms / 1000)
        return root_node, cwd
