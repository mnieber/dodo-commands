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
        parser.add_argument(
            '--project-name',
            help='Compare to files from an alternative project'
        )

    def handle_imp(self, file, project_name, **kwargs):  # noqa
        project_dir = self.get_config("/ROOT/project_dir", "")

        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.dodo_commands/config"))

        diff_tool = config.get("DodoCommands", "diff_tool")
        res_dir = os.path.join(project_dir, "dodo_commands", "res")

        if project_name:
            ref_project_dir = os.path.abspath(
                os.path.join(project_dir, "..", project_name)
            )
            original_file = os.path.join(
                ref_project_dir, "dodo_commands", "res", file
            )
        else:
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
