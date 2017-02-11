"""Finds a directory or file inside the current project."""
from . import DodoCommand
from dodo_commands.framework.config import (CommandPath, get_project_dir)
import os
import sys


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument(
            'what',
            nargs='?',
            help=(
                'Print the value of /ROOT/<what>_dir. For example: ' +
                '"dodo which src" prints the value of /ROOT/src_dir.')
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--config',
            action="store_true",
            help='Print where the config file is')
        group.add_argument(
            '--script',
            help='Print where the dodo command script with given name is')

    def handle_imp(self, what, config, script, **kwargs):
        project_dir = get_project_dir()
        if config:
            print(
                os.path.join(
                    project_dir, "dodo_commands", "res", "config.yaml"
                )
            )
        elif script:
            command_path = CommandPath(project_dir)
            for item in command_path.items:
                script_path = os.path.join(
                    item.full_path, script + ".py"
                )
                if os.path.exists(script_path):
                    sys.stdout.write(script_path + "\n")
        elif what:
            sys.stdout.write(self.get_config("/ROOT/%s_dir" % what) + "\n")
        else:
            sys.stdout.write(self.get_config("/ROOT/project_name") + "\n")
