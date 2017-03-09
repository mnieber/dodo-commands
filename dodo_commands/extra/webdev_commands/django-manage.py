"""Run a django-manage command."""
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    decorators = ['docker']

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'manage_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(  # noqa
        self, manage_args, *args, **kwargs
    ):
        self.runcmd(
            [
                self.get_config("/DJANGO/python"),
                "manage.py",
            ] + remove_trailing_dashes(manage_args),
            cwd=self.get_config("/DJANGO/src_dir")
        )
