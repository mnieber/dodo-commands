"""Script for activating/creating a project in the projects folder."""
import argparse
import os
from plumbum import local
from plumbum.cmd import ln


class DefaultsInstaller:
    """Adds subdirectories to defaults/commands and defaults/projects."""

    def _args(self):
        """Get command line args."""
        parser = argparse.ArgumentParser()

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--git',
            action="store_true",
            dest="use_git",
            help='Use a git repository'
        )
        group.add_argument(
            '--ln',
            action="store_false",
            dest="use_git",
            help='Use a symlink'
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--commands')
        group.add_argument('--projects')
        return parser.parse_args()

    def _install(self, dest_folder, url, use_git):
        """Install resource 'url' into dest_folder."""
        if use_git:
            with local.cwd(dest_folder):
                local['git']['clone', url]()
        else:
            ln("-s", os.path.abspath(url), dest_folder)

    def _install_commands(self, url, use_git):
        """Install the folder with the default commands."""
        commands_dir = os.path.join(
            self.source_folder, "defaults", "commands"
        )
        self._install(commands_dir, url, use_git)

    def _install_projects(self, url, use_git):
        """Install the folder with the default commands."""
        projects_dir = os.path.join(
            self.source_folder, "defaults", "projects"
        )
        self._install(projects_dir, url, use_git)

    def run(self):
        """Activate or create a project in the projects folder."""
        bin_folder = os.path.dirname(__file__)
        self.source_folder = os.path.dirname(bin_folder)
        args = self._args()

        url, install = (
            (args.commands, self._install_commands)
            if args.commands else
            (args.projects, self._install_projects)
        )

        if not args.use_git and not os.path.exists(url):
            print("Error: path not found: %s" % url)
            return

        install(url, args.use_git)
