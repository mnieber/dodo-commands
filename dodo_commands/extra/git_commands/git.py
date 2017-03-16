"""Init the source files from the configured git url."""

from . import DodoCommand
import argparse


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'git_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(  # noqa
        self, *args, **kwargs
    ):
        self.runcmd(
            [
                "git",
            ] + kwargs['git_args'],
            cwd=self.get_config("/ROOT/src_dir")
        )
