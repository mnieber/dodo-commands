"""Pull the latest version of the Dodo Commands system."""

from . import DodoCommand
from dodo_commands.framework import call_command, CommandError
import os


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--check-version', action='store_true')

    def handle_imp(self, check_version, **kwargs):  # noqa
        default_project_dir = self.get_config(
            "/ROOT/project_dir", "defaults/project"
        )

        if not os.path.exists(default_project_dir):
            raise CommandError(
                "No default project dir: %s" % default_project_dir
            )

        self.runcmd(
            [
                "git",
                "pull",
            ],
            cwd=default_project_dir
        )

        if check_version:
            call_command('check-config-version', **kwargs)
