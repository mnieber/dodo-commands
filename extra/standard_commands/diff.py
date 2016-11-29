"""Show diff for a file in the Dodo Commands system directory."""

from . import DodoCommand
import ConfigParser
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
        system_dir = self.get_config("/ROOT/system_dir", "")
        project_name = self.get_config("/ROOT/project_name", "")

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(system_dir, "dodo_commands.config"))

        diff_tool = config.get("DodoCommands", "diff_tool")
        dodo_commands_dir = os.path.join(project_dir, "dodo_commands")

        original_file = os.path.join(
            system_dir, "defaults", "projects", project_name, file)
        copied_file = os.path.join(dodo_commands_dir, file)

        self.runcmd(
            [diff_tool, original_file, copied_file],
            cwd=dodo_commands_dir
        )
