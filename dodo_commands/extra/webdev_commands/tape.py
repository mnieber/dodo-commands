# noqa
import argparse
import os
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


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
        jsx_dir = os.path.join(self.get_config("/ROOT/src_dir"), "jsx")
        assert os.path.exists(jsx_dir)

        self.runcmd(
            [
                self.get_config("/TAPE/tape_run"),
                self.get_config("/TAPE/bundle_file"),
            ] + remove_trailing_dashes(tape_args),
            cwd=jsx_dir
        )
