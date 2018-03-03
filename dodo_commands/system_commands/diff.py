"""Show diff for a file in the Dodo Commands system directory."""

from . import DodoCommand, CommandError
from six.moves import configparser
import os
from dodo_commands.framework.config import get_project_dir

class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument(
            'file',
            nargs='?',
            help='Show diff for this file'
        )
        parser.add_argument(
            '--project-name',
            help='Compare to files from an alternative project'
        )
        parser.add_argument(
            '--defaults-dir',
            help='Set the relative path to the default config files'
        )

    def _diff_tool(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.dodo_commands/config"))
        return config.get("DodoCommands", "diff_tool")

    def handle_imp(self, file, project_name, defaults_dir, **kwargs):  # noqa
        file = file or '.'
        project_dir = get_project_dir()
        default_project_path = os.path.join(
            project_dir, "dodo_commands", "default_project"
        )

        if defaults_dir:
            if os.path.exists(default_project_path):
                raise CommandError(
                    "The --default-dir option was supplied, " +
                    "but the symlink %s already exists"
                    % default_project_path
                )

            target_dir = os.path.join(project_dir, defaults_dir)
            if not os.path.exists(target_dir):
                raise CommandError(
                    "The --default-dir option was supplied, " +
                    "but the target directory %s does not exist"
                    % target_dir
                )

            self.runcmd(["ln", "-s", target_dir, default_project_path])

        if project_name:
            ref_project_dir = os.path.abspath(
                os.path.join(project_dir, "..", project_name)
            )
            original_file = os.path.join(ref_project_dir, file)
            copied_file = os.path.join(project_dir, file)
        else:
            original_file = os.path.realpath(
                os.path.join(default_project_path, file)
            )
            copied_file = os.path.join(project_dir, "dodo_commands", "res", file)

        self.runcmd([self._diff_tool(), original_file, copied_file])
