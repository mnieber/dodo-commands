# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand


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
        tape_args = tape_args[1:] if tape_args[:1] == ['-'] else tape_args

        self.runcmd(
            [
                self.get_config("/TAPE/tape", "tape"),
                self.get_config("/TAPE/glob")
            ] + tape_args,
            cwd=self.get_config("/TAPE/src_dir")
        )
