# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    decorators = ["docker"]
    docker_options = [
        '--name=pytest',
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'pytest_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, pytest_args, **kwargs):  # noqa
        if pytest_args[:1] == ['-']:
            pytest_args = pytest_args[1:]

        self.runcmd(
            [
                self.get_config("/PYTEST/pytest"),
            ] + pytest_args,
            cwd=self.get_config("/PYTEST/src_dir")
        )
