"""Run a django-manage command."""
import argparse
from dodo_commands.extra.standard_commands import DodoCommand


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
        if manage_args[:1] == ['-']:
            manage_args = manage_args[1:]

        self.runcmd(
            [
                self.get_config("/DJANGO/python"),
                "manage.py",
            ] + manage_args,
            cwd=self.get_config("/DJANGO/src_dir")
        )
