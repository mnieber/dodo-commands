"""Finds a directory or file inside the current project."""
from . import DodoCommand
from dodo_commands.framework.config import (
    CommandPath, get_project_dir
)
import os
import sys


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--src',
            action="store_true",
            dest="which_src",
            help='Print where the src directory is'
        )
        group.add_argument(
            '--build',
            action="store_true",
            dest="which_build",
            help='Print where the build directory is'
        )
        group.add_argument(
            '--project',
            action="store_true",
            dest="which_project",
            help='Print where the project directory is'
        )
        group.add_argument(
            '--config',
            action="store_true",
            dest="which_config",
            help='Print where the config file is'
        )
        group.add_argument(
            '--script',
            dest="which_script",
            help='Print where the dodo command script with given name is'
        )
        group.add_argument(
            '--system',
            action="store_true",
            dest="which_system",
            help='Print where the dodo commands system folder is'
        )

    def handle_imp(  # noqa
        self, which_src, which_build, which_project, which_config,
        which_script, which_system, **kwargs
    ):
        build_dir = self.get_config("/ROOT/build_dir", "")
        src_dir = self.get_config("/ROOT/src_dir", "")
        project_dir = self.get_config("/ROOT/project_dir", get_project_dir())

        if which_src:
            print(src_dir)
        elif which_build:
            print(build_dir)
        elif which_project:
            print(project_dir)
        elif which_config:
            print(os.path.join(project_dir, "dodo_commands", "config.yaml"))
        elif which_system:
            print(self.get_config("/ROOT/system_dir"))
        elif which_script:
            command_path = CommandPath(project_dir)
            for item in command_path.items:
                script_path = os.path.join(
                    item.full_path, which_script + ".py"
                )
                if os.path.exists(script_path):
                    sys.stdout.write(script_path + "\n")
        else:
            print(self.get_config("/ROOT/project_name"))
