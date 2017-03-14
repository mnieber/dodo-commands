# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
import os

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']
    docker_options = [
        '--name=node-sass',
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--watch', action="store_true")
        parser.add_argument(
            'nodesass_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, watch, nodesass_args, **kwargs):  # noqa
        nodesass = self.get_config("/SASS/nodesass", "node-sass")
        self.runcmd(
            [
                "mkdir",
                "-p",
                os.path.dirname(self.get_config("/SASS/output_file"))
            ]
        )

        self.runcmd(
            [
                nodesass,
                self.get_config("/SASS/src_file"),
                self.get_config("/SASS/output_file")
            ] + nodesass_args
        )

        self.runcmd(
            [
                nodesass,
                self.get_config("/SASS/src_file"),
                self.get_config("/SASS/output_file")
            ] + nodesass_args + (["-w"] if watch else [])
        )
