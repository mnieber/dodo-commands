"""Run an arbitrary command line."""
from . import DodoCommand
import os


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('run_args')

    def handle_imp(self, run_args, **kwargs):  # noqa
        args = [os.path.expanduser(a) for a in run_args.split()]
        self.runcmd(args)
