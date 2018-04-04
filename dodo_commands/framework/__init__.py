import argcomplete
from argparse import ArgumentParser
from collections import defaultdict
import ruamel.yaml
import os
import pkgutil
import subprocess
import sys
import traceback
from importlib import import_module
from dodo_commands.framework.util import query_yes_no
from dodo_commands.framework.config import (
    CommandPath, get_project_dir, ConfigLoader
)
from dodo_commands.framework.singleton import Dodo
from dodo_commands.framework.command_error import CommandError  # noqa



def get_version():  # noqa
    return "0.13.5"


def execute_script(module_dir, name):
    """
    Return the Command class instance for module_dir and name.

    Given a command name and module directory, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    """
    def install_packages(meta_data_filename):
        """Pip install packages found in meta_data_filename."""
        with open(meta_data_filename) as f:
            meta_data = ruamel.yaml.round_trip_load(f.read())
            print("This command wants to install additional packages:\n")
            print(meta_data['requirements'])
            if query_yes_no("Install (yes), or abort (no)?"):
                print("\n--- Installing from %s ---" % meta_data_filename)
                pip = os.path.join(
                    get_project_dir(),
                    "dodo_commands/env/bin/pip"
                )
                subprocess.check_call(
                    [pip, "install"] + meta_data['requirements'])
                print("--- Done ---\n\n")
            else:
                sys.exit(1)

    package_path = module_dir.replace("/", ".")
    import_path = '%s.%s' % (package_path, name)
    if module_dir in ("", None, "."):
        import_path = name

    try:
        import_module(import_path)
    except ImportError as e:
        try:
            base_path = import_module(package_path).__path__[0]
            meta_data_filename = os.path.join(base_path, name + ".meta")
            if os.path.exists(meta_data_filename):
                install_packages(meta_data_filename)
                import_module(import_path)
            else:
                print(traceback.print_exc(e))
                sys.exit(1)
        except ImportError as e:
            print(traceback.print_exc(e))
            sys.exit(1)


def get_commands():
    """
    Return a dictionary mapping command names to their Python module directory.
    The dictionary is in the format {command_name: module_name}.
    """
    result = {}
    command_path = CommandPath(ConfigLoader().load())
    command_path.extend_sys_path()
    for item in command_path.items:
        commands = [
            name for _, name, is_pkg in pkgutil.iter_modules([item.full_path])
            if not is_pkg and not name.startswith('_')
        ]
        for command in commands:
            result[command] = item.module_path
    return result


class ManagementUtility(object):
    """Internal helper class for executing commands."""

    def __init__(self, argv):  # noqa
        self.argv = argv
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False, commands=None):
        """Return the script's main help text, as a string."""
        if commands is None:
            commands = get_commands()

        if commands_only:
            usage = sorted(commands.keys())
        else:
            usage = [
                "",
                "Version %s (%s --version)." % (
                    get_version(), self.prog_name
                ),
                "Type '%s help <subcommand>' for help on "
                "a specific subcommand." % self.prog_name,
                "Available subcommands (dodo help --commands):",
            ]
            commands_dict = defaultdict(lambda: [])
            for name, app in commands.items():
                app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
            for app in sorted(commands_dict.keys()):
                usage.append("")
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)

        return '\n'.join(usage)

    def execute(self):
        """
        Execute subcommand.

        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        commands = get_commands()

        if "_ARGCOMPLETE" in os.environ:
            words = os.environ['COMP_LINE'].split()
            subcommand = words[1]

            if subcommand not in commands:
                parser = ArgumentParser()
                parser.add_argument(
                    'command',
                    choices=[x for x in commands.keys()]
                )
                argcomplete.autocomplete(parser)

            os.environ['COMP_LINE'] = ' '.join(words[:1] + words[2:])
            os.environ['COMP_POINT'] = str(
                int(os.environ['COMP_POINT']) - (len(subcommand) + 1)
            )
        else:
            try:
                subcommand = self.argv[1]
            except IndexError:
                subcommand = 'help'  # Display help if no arguments were given.

        if subcommand == '--version':
            sys.stdout.write(get_version() + '\n')
        elif subcommand == 'help':
            if '--commands' in sys.argv:
                sys.stdout.write(
                    self.main_help_text(
                        commands_only=True, commands=commands
                    ) + '\n'
                )
            else:
                sys.stdout.write(self.main_help_text() + '\n')
        else:
            if subcommand not in commands:
                print("Unknown dodo command: %s" % subcommand)
                sys.exit(1)

            module_dir = commands[subcommand]
            Dodo.command_name = subcommand

            try:
                execute_script(module_dir, subcommand)
            except KeyboardInterrupt:
                print('\n')
                sys.exit(1)
            except Exception as e:
                if (
                    getattr(Dodo.args, 'traceback', False) or
                    not isinstance(e, CommandError)
                ):
                    raise
                sys.stderr.write('%s: %s\n' % (e.__class__.__name__, e))
                sys.exit(1)


def execute_from_command_line(argv):
    """A simple method that runs a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
