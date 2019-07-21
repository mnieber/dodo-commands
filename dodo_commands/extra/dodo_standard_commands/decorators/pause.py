"""Pauses the execution."""
import time


class Decorator:
    def add_arguments(self, parser):  # override
        parser.add_argument(
            '--pause-ms',
            type=int,
            help="Pause in milliseconds before continuing")

    def modify_args(self, command_line_args, root_node, cwd):  # override
        if getattr(command_line_args, 'pause_ms', 0):
            time.sleep(command_line_args.pause_ms / 1000)
        return root_node, cwd
