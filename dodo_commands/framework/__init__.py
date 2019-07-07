import argcomplete
from argparse import ArgumentParser
from collections import defaultdict
import os
import sys
from dodo_commands.framework.config import (load_global_config_parser,
                                            get_command_path, ConfigLoader)
from dodo_commands.framework.singleton import Dodo, DecoratorScope, ConfigArg  # noqa
from dodo_commands.framework.command_error import CommandError  # noqa
from dodo_commands.framework.command_map import get_command_map, execute_script


def get_version():  # noqa
    return "0.26.0"


class ManagementUtility(object):
    """Internal helper class for executing commands."""

    def __init__(self):  # noqa
        self.prog_name = os.path.basename(sys.argv[0])

    def main_help_text(self, command_map, commands_only=False):
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
                "Available commands (dodo help --commands):\n",
            ]

            max_name_size = -1
            command_groups = defaultdict(lambda: [])
            for command_name, command_map_item in command_map.items():
                max_name_size = max(max_name_size, len(command_name))
                command_groups[command_map_item.group].append(command_name)

            groups = sorted(list(command_groups.values()),
                            key=lambda x: len(x),
                            reverse=True)
            for group in groups:
                group.append("")

            col_width = max_name_size + 10
            rows, cols = os.popen('stty size', 'r').read().split()
            nr_cols = max(1, int(int(cols) / col_width))

            head, tail = groups[:nr_cols], groups[nr_cols:]
            while any([x is not None for x in head]):
                names = []
                for group_idx, group in enumerate(head):
                    names.append('' if group is None else group.pop(0))
                    if group is not None and len(group) == 0:
                        head[group_idx] = (tail.pop(0) if tail else None)
                usage.append("".join(name.ljust(col_width) for name in names))

        return '\n'.join(usage)

    def _handle_exception(self, e):
        if '--traceback' in sys.argv or not isinstance(e, CommandError):
            raise
        sys.stderr.write('%s: %s\n' % (e.__class__.__name__, e))
        sys.exit(1)

    def _aliases(self, config):
        result = list(config['ROOT'].get('aliases', {}).items())
        global_config = load_global_config_parser()
        if global_config.has_section('alias'):
            result.extend(global_config.items('alias'))
        return result

    def _handle_arg_complete(self, config, command_map):
        words = os.environ['COMP_LINE'].split()
        command_name = words[1]

        choices = [x for x in command_map.keys()]
        for key, val in self._aliases(config):
            choices.append(key)

        if command_name not in choices:
            parser = ArgumentParser()
            parser.add_argument('command', choices=choices)
            argcomplete.autocomplete(parser)

        os.environ['COMP_LINE'] = ' '.join(words[:1] + words[2:])
        os.environ['COMP_POINT'] = str(
            int(os.environ['COMP_POINT']) - (len(command_name) + 1))

        return command_name

    def _find_alias(self, config, command_name):
        for key, val in self._aliases(config):
            if key == command_name:
                return val.split()
        return None

    def execute(self):
        """
        Execute command.

        Given the command-line arguments, this figures out which command is
        being run, creates a parser appropriate to that command, and runs it.
        """
        try:
            config = ConfigLoader().load()
            command_map = get_command_map(get_command_path(config))
        except Exception as e:
            self._handle_exception(e)

        if "_ARGCOMPLETE" in os.environ:
            command_name = self._handle_arg_complete(config, command_map)
        else:
            try:
                command_name = sys.argv[1]
            except IndexError:
                command_name = 'help'  # Display help if no arguments were given.

        if command_name == '--version':
            sys.stdout.write(get_version() + '\n')
        elif command_name == 'help':
            sys.stdout.write(
                self.main_help_text(command_map,
                                    commands_only=('--commands' in sys.argv)) +
                '\n')
        else:
            alias = self._find_alias(config, command_name)
            if alias and alias[0] in command_map:
                command_name = alias[0]
                sys.argv = sys.argv[:1] + alias + sys.argv[2:]

            if command_name not in command_map:
                print("Unknown dodo command: %s" % command_name)
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
    utility = ManagementUtility()
    utility.execute()
