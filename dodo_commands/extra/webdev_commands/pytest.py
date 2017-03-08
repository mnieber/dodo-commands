# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


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
        self.runcmd(
            [
                self.get_config("/PYTEST/pytest"),
            ] + remove_trailing_dashes(pytest_args),
            cwd=self.get_config("/PYTEST/src_dir")
        )
