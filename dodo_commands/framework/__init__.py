import argcomplete
from argparse import ArgumentParser
from collections import defaultdict
import os
import sys
from dodo_commands.framework.config import load_global_config_parser, get_command_path
from dodo_commands.framework.singleton import Dodo, DecoratorScope, ConfigArg  # noqa
from dodo_commands.framework.command_error import CommandError  # noqa
from dodo_commands.framework.command_map import get_command_map, execute_script


def get_version():  # noqa
    return "0.23.0"


class ManagementUtility(object):
    """Internal helper class for executing commands."""

    def __init__(self, argv):  # noqa
        self.argv = argv
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False, command_map=None):
        """Return the script's main help text, as a string."""
        if command_map is None:
            command_map = get_command_map(get_command_path())

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
            command_map = get_command_map(get_command_path())
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
                execute_script(command_map, command_name)
            except KeyboardInterrupt:
                print('\n')
                sys.exit(1)
            except Exception as e:
                self._handle_exception(e)


def execute_from_command_line(argv):
    """A simple method that runs a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
