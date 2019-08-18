import argcomplete
from argparse import ArgumentParser
import os
import sys

from dodo_commands.framework.singleton import Dodo
from dodo_commands.framework.alias import get_aliases, find_alias
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.version import get_version
from dodo_commands.framework.command_path import get_command_path
from dodo_commands.framework.command_map import get_command_map, execute_script


def _handle_arg_complete(command_map, aliases):
    words = os.environ['COMP_LINE'].split()
    command_name = words[1]

    choices = [x for x in command_map.keys()]
    for key, val in aliases:
        choices.append(key)

    if command_name not in choices:
        parser = ArgumentParser()
        parser.add_argument('command', choices=choices)
        argcomplete.autocomplete(parser)

    os.environ['COMP_LINE'] = ' '.join(words[:1] + words[2:])
    os.environ['COMP_POINT'] = str(
        int(os.environ['COMP_POINT']) - (len(command_name) + 1))

    return command_name


def _handle_exception(e):
    if '--traceback' in sys.argv or not isinstance(e, CommandError):
        raise
    sys.stderr.write('%s: %s\n' % (e.__class__.__name__, e))
    sys.exit(1)


def _command_name(command_map, aliases):
    if "_ARGCOMPLETE" in os.environ:
        return _handle_arg_complete(command_map, aliases)
    if len(sys.argv) >= 2:
        return sys.argv[1]
    return 'help'


def execute_from_command_line(argv):
    try:
        command_map = get_command_map(get_command_path(Dodo.get_config()))
    except Exception as e:
        _handle_exception(e)

    aliases = get_aliases(Dodo.get_config())
    command_name = _command_name(command_map, aliases)

    if command_name == '--version':
        sys.stdout.write(get_version() + '\n')
        sys.exit(0)

    alias = find_alias(command_name, aliases)
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
        _handle_exception(e)
