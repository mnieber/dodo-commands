# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']
    docker_options = [
        '--name=autoless',
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'autoless_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, autoless_args, **kwargs):  # noqa
        autoless = self.get_config("/LESS/autoless", "autoless")
        self.runcmd(
            [
                "mkdir",
                "-p",
                self.get_config("/LESS/output_dir")
            ]
        )

        self.runcmd(
            [
                autoless,
                ".",
                self.get_config("/LESS/output_dir")
            ] + autoless_args,
            cwd=self.get_config("/LESS/src_dir")
        )
