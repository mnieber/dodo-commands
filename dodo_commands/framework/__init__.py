import argcomplete
from argparse import ArgumentParser
from collections import defaultdict
import os
import sys
from dodo_commands.framework.python_command_handler import PythonCommandHandler
from dodo_commands.framework.yaml_command_handler import YamlCommandHandler
from dodo_commands.framework.config import (ConfigLoader,
                                            load_global_config_parser)
from dodo_commands.framework.singleton import Dodo, DecoratorScope, ConfigArg  # noqa
from dodo_commands.framework.command_error import CommandError  # noqa


def get_version():  # noqa
    return "0.22.0"


def _log(string):
    with open('/tmp/.dodo.log', 'w') as ofs:
        ofs.write(string + '\n')


def execute_script(command_map_item, command_name):
    """
    Executes the script associated with command_name by importing its package.
    The script is assumed to have an entry point that is executed if
    Dodo.is_main(__name__) is True.
    """
    Dodo.command_name = command_name

    if command_map_item.extension == 'py':
        Dodo.package_path = command_map_item.package_path
        PythonCommandHandler().execute(command_map_item, command_name)
    elif command_map_item.extension == 'yaml':
        YamlCommandHandler().execute(command_map_item, command_name)
    else:
        raise Exception("Logical error")


def get_command_map():
    """
    Return a dictionary mapping command names to their Python module directory.
    The dictionary is in the format {command_name: module_name}.
    """
    config = ConfigLoader().load()
    command_map = {}

    PythonCommandHandler().add_commands_to_map(config, command_map)
    YamlCommandHandler().add_commands_to_map(config, command_map)
    return command_map


class ManagementUtility(object):
    """Internal helper class for executing commands."""

    def __init__(self, argv):  # noqa
        self.argv = argv
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False, command_map=None):
        """Return the script's main help text, as a string."""
        if command_map is None:
            command_map = get_command_map()

        if commands_only:
            usage = sorted(command_map.keys())
        else:
            usage = [
                "",
                "Version %s (%s --version)." % (get_version(), self.prog_name),
                "Type '%s help <command>' for help on "
                "a specific command." % self.prog_name,
                "Available commands (dodo help --commands):",
            ]
            command_groups = defaultdict(lambda: [])
            for command_name, command_map_item in command_map.items():
                command_groups[command_map_item.group].append(command_name)
            for package_path in sorted(command_groups.keys()):
                usage.append("")
                for command_name in sorted(command_groups[package_path]):
                    usage.append("    %s" % command_name)

        return '\n'.join(usage)

    def _handle_exception(self, e):
        if '--traceback' in sys.argv or not isinstance(e, CommandError):
            raise
        sys.stderr.write('%s: %s\n' % (e.__class__.__name__, e))
        sys.exit(1)

    def _handle_arg_complete(self, command_map):
        words = os.environ['COMP_LINE'].split()
        command_name = words[1]

        if command_name not in command_map:
            parser = ArgumentParser()
            parser.add_argument('command',
                                choices=[x for x in command_map.keys()])
            argcomplete.autocomplete(parser)

        os.environ['COMP_LINE'] = ' '.join(words[:1] + words[2:])
        os.environ['COMP_POINT'] = str(
            int(os.environ['COMP_POINT']) - (len(command_name) + 1))

        return command_name

    def _find_alias(self, command_name):
        global_config = load_global_config_parser()
        if global_config.has_section('alias'):
            for key, val in global_config.items('alias'):
                if key == command_name:
                    return val
        return None

    def execute(self):
        """
        Execute command.

        Given the command-line arguments, this figures out which command is
        being run, creates a parser appropriate to that command, and runs it.
        """
        try:
            command_map = get_command_map()
        except Exception as e:
            self._handle_exception(e)

        if "_ARGCOMPLETE" in os.environ:
            command_name = self._handle_arg_complete(command_map)
        else:
            try:
                command_name = self.argv[1]
            except IndexError:
                command_name = 'help'  # Display help if no arguments were given.

        if command_name == '--version':
            sys.stdout.write(get_version() + '\n')
        elif command_name == 'help':
            if '--commands' in sys.argv:
                sys.stdout.write(
                    self.main_help_text(commands_only=True,
                                        command_map=command_map) + '\n')
            else:
                sys.stdout.write(self.main_help_text() + '\n')
        else:
            if command_name not in command_map:
                alias = self._find_alias(command_name)
                if alias and alias in command_map:
                    command_name = alias
                else:
                    print("Unknown dodo command: %s" % (alias or command_name))
                    sys.exit(1)

            try:
                execute_script(command_map[command_name], command_name)
            except KeyboardInterrupt:
                print('\n')
                sys.exit(1)
            except Exception as e:
                self._handle_exception(e)


def execute_from_command_line(argv):
    """A simple method that runs a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
