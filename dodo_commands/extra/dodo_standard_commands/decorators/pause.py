"""Pauses the execution."""
import time


class Decorator:  # noqa
    def add_arguments(self, parser):  # noqa
        parser.add_argument(
            '--pause-ms',
            type=int,
            help="Pause in milliseconds before continuing")

    def modify_args(self, dodo_args, root_node, cwd):  # noqa
        if getattr(dodo_args, 'pause_ms', 0):
            time.sleep(dodo_args.pause_ms / 1000)
        return root_node, cwd
