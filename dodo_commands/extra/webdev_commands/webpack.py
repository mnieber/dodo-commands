"""Run the webpack command."""
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    decorators = ['docker']
    docker_options = [
        '--name=webpack',
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--watch', action="store_true")
        parser.add_argument(
            'webpack_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, watch, webpack_args, **kwargs):  # noqa
        webpack = self.get_config("/WEBPACK/webpack", "webpack")
        webpack_args = webpack_args or []

        self.runcmd(
            [webpack]
            + (["--watch-stdin"] if watch else [])
            + remove_trailing_dashes(webpack_args),
            cwd=self.get_config("/WEBPACK/webpack_dir")
        )
