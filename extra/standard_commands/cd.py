"""Print the command line to cd to a folder inside the project folder."""
from . import DodoCommand
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
            dest="cd_to_src",
            help='cd to the src directory'
        )
        group.add_argument(
            '--build',
            action="store_true",
            dest="cd_to_build",
            help='cd to the build directory'
        )
        group.add_argument(
            '--install',
            action="store_true",
            dest="cd_to_install",
            help='cd to the install directory'
        )
        group.add_argument(
            '--system',
            action="store_true",
            dest="cd_to_system",
            help='cd to the dodo commands system folder'
        )

    def handle_imp(  # noqa
        self, cd_to_src, cd_to_build, cd_to_install, cd_to_system, **kwargs
    ):
        sys.stdout.write("cd ")
        if cd_to_src:
            src_dir = self.get_config("/ROOT/src_dir")
            print src_dir
        elif cd_to_build:
            build_dir = self.get_config("/ROOT/build_dir")
            print build_dir
        elif cd_to_install:
            project_dir = self.get_config("/ROOT/project_dir")
            print os.path.join(project_dir, "install")
        elif cd_to_system:
            print self.get_config("/ROOT/system_dir")
        else:
            print self.get_config("/ROOT/project_dir")
