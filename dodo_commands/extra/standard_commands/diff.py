"""Show diff for a file in the Dodo Commands system directory."""

from . import DodoCommand
from six.moves import configparser
import os


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument(
            'file',
            help='Show diff for this file'
        )

    def handle_imp(self, file, **kwargs):  # noqa
        project_dir = self.get_config("/ROOT/project_dir", "")

        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.dodo_commands/config"))

        diff_tool = config.get("DodoCommands", "diff_tool")
        res_dir = os.path.join(project_dir, "dodo_commands", "res")

        original_file = os.path.realpath(
            os.path.join(
                project_dir, "dodo_commands", "default_project", file
            )
        )
        copied_file = os.path.join(res_dir, file)

        self.runcmd(
            [diff_tool, original_file, copied_file],
            cwd=res_dir
        )
