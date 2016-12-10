"""Run a django-manage command."""
import argparse
from dodo_commands.defaults.commands.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    decorators = ['docker']

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            '--args',
            dest="manage_args",
            required=False,
            default=[],
            nargs=argparse.REMAINDER
        )

    def handle_imp(  # noqa
        self, manage_args, **kwargs
    ):
        self.runcmd(
            [
                "python",
                "manage.py",
                manage_args
            ],
            cwd=self.get_config("/DJANGO/src_dir")
        )
