"""Finds a directory or file inside the current project."""
from . import DodoCommand
from dodo_commands.framework.config import (CommandPath, get_project_dir)
import os
from six.moves import configparser
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
            '--global-config',
            action="store_true",
            help='Print where the global config file is')
        group.add_argument(
            '--script',
            help='Print where the dodo command script with given name is')
        group.add_argument(
            '--dir',
            dest='directory',
            help='Finds the X_dir value in the configuration, where X is the given option value')
        group.add_argument(
            '--decorators',
            action="store_true",
            help='Prints which command decorators are available')
        group.add_argument(
            '--projects',
            action="store_true",
            help='Prints which projects are available')

    def _which_script(self, script):
        command_path = CommandPath(self.config)
        for item in command_path.items:
            script_path = os.path.join(
                item.full_path, script + ".py"
            )
            if os.path.exists(script_path):
                return script_path
        return None

    def _which_dir(self, directory):
        return self.get_config("/ROOT/%s_dir" % directory, None)

    def _projects_dir(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.dodo_commands/config"))
        return os.path.expanduser(config.get("DodoCommands", "projects_dir"))

    def handle_imp(self, what, config, global_config, script, directory, decorators, projects, **kwargs):
        if config:
            print(
                os.path.join(
                    get_project_dir(), "dodo_commands", "res", "config.yaml"
                )
            )
        elif global_config:
            sys.stdout.write(os.path.expanduser('~/.dodo_commands/config\n'))
        elif script:
            sys.stdout.write(self._which_script(script) + "\n")
        elif directory:
            sys.stdout.write(self._which_dir(directory) + "\n")
        elif decorators:
            sys.stdout.write(", ".join(sorted(self.all_decorators().keys())) + "\n")
        elif projects:
            projects = [
                x for x in os.listdir(self._projects_dir())
                if os.path.isdir(os.path.join(self._projects_dir(), x, "dodo_commands", "res"))
            ]
            sys.stdout.write("\n".join(sorted(projects)) + "\n")
        elif what:
            x = self._which_script(what) or self._which_dir(what)
            if x:
                sys.stdout.write(x + "\n")
        else:
            sys.stdout.write(self.get_config("/ROOT/project_name") + "\n")
