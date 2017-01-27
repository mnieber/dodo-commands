"""Script for activating/creating a project in the projects dir."""
import argparse
import os
import sys

from plumbum import local
from plumbum.cmd import ln
from plumbum.commands.processes import ProcessExecutionError


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

    def _report_error(self, msg):
        sys.stderr.write(msg + os.linesep)

    def _install(self, dest_dir, url, use_git):
        """Install resource 'url' into dest_dir."""
        try:
            if use_git:
                with local.cwd(dest_dir):
                    local['git']['clone', url]()
            else:
                if not os.path.exists(url):
                    self._report_error("Error: path not found: %s" % url)
                    return False
                ln("-s", os.path.abspath(url), dest_dir)
        except ProcessExecutionError:
            if use_git:
                self._report_error((
                    "Could not clone into %s. Check that the " +
                    "destination does not already exist.") % dest_dir
                )
            else:
                dest_path = os.path.join(dest_dir, os.path.basename(url))
                msg = (
                    "%s already exists (no changes were made)." % dest_path
                    if os.path.exists(dest_path) else
                    "Error: could not create a symlink in %s." % dest_dir
                )
                self._report_error(msg)
            return False

        return True

    def _install_commands(self, url, use_git):
        """Install the dir with the default commands."""
        commands_dir = os.path.join(
            self.source_dir, "defaults", "commands"
        )
        return self._install(commands_dir, url, use_git)

    def _install_projects(self, url, use_git):
        """Install the dir with the default commands."""
        projects_dir = os.path.join(
            self.source_dir, "defaults", "projects"
        )
        return self._install(projects_dir, url, use_git)

    def run(self):
        """Activate or create a project in the projects dir."""
        bin_dir = os.path.dirname(__file__)
        self.source_dir = os.path.dirname(bin_dir)
        args = self._args()

        url, install = (
            (args.commands, self._install_commands)
            if args.commands else
            (args.projects, self._install_projects)
        )

        install(url, args.use_git)


def main():
    DefaultsInstaller().run()

