# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    decorators = ["docker"]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'pytest_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, pytest_args, **kwargs):  # noqa
        self.runcmd(
            [
                self.get_config("/PYTEST/pytest"),
            ] + pytest_args,
            cwd=self.get_config("/PYTEST/src_dir")
        )
