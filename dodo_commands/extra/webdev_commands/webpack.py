"""Run the webpack command."""
import argparse
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    decorators = ['docker']

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            '--args',
            dest="webpack_args",
            required=False,
            default=[],
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, webpack_args, **kwargs):  # noqa
        webpack = self.get_config("/WEBPACK/webpack", "webpack")
        self.runcmd(
            [webpack, "--watch-stdin", webpack_args],
            cwd=self.get_config("/WEBPACK/webpack_dir")
        )
