"""Pauses the execution."""
import time


class Decorator:  # noqa
    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--pause-ms',
            type=int,
            help="Pause in milliseconds before continuing"
        )

    def handle(self, decorated, pause_ms, **kwargs):  # noqa
        if pause_ms:
            time.sleep(pause_ms / 1000)

    def modify_args(self, decorated, args, cwd):  # noqa
        return args, cwd
