"""Init the source files from the configured git url."""

from . import DodoCommand
import os


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--init',
            action='store_true',
        )
        group.add_argument(
            '--status',
            action='store_true',
            dest='do_status'
        )

        parser.add_argument(
            '--depth',
            type=int,
            default=0,
            help="Depth for cloning repositories"
        )

    def handle_imp(  # noqa
        self, init, do_status, depth, **kwargs
    ):
        clone_dir = self.get_config("/GIT/clone_dir")
        if init:
            self.runcmd(
                [
                    "git",
                    "clone",
                    self.get_config('/GIT/url'),
                    os.path.basename(clone_dir)
                ] + (["--depth", depth] if depth else []),
                cwd=os.path.dirname(clone_dir)
            )

        if do_status:
            self.runcmd(["git", "status"], cwd=clone_dir)
