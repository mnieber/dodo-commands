# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.util import remove_trailing_dashes
import json
import os


class Command(DodoCommand):  # noqa
    help = ""
    decorators = ["docker"]
    docker_options = [
        '--name=tape',
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'tape_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, tape_args, **kwargs):  # noqa
        stats_file = os.path.join(
            self.get_config("/ROOT/src_dir"),
            "webpack/webpack-stats.json"
        )
        stats = json.loads(open(stats_file).read())
        bundle = os.path.join(
            self.get_config("/VIRT_ROOT/src_dir"),
            "static/bundles",
            stats["chunks"]["main"][0]["name"]
        )

        self.runcmd(
            [
                "tape-run",
                bundle,
            ] + remove_trailing_dashes(tape_args),
            cwd=self.get_config("/TAPE/src_dir")
        )
