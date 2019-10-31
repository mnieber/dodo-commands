import argcomplete
from argparse import ArgumentParser
import os
import sys

from dodo_commands.framework.singleton import Dodo
from dodo_commands.framework.alias import get_command_aliases, find_command_alias
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.version import get_version
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.command_map import get_command_map, execute_script
from dodo_commands.framework.inferred_commands import get_inferred_commands
from dodo_commands.framework.config import load_config


def _split_prefix(command_name):
    pos = command_name.rfind('.')
    if pos:
        return command_name[:pos + 1], command_name[pos + 1:]
    return command_name


def _handle_arg_complete(command_map, command_aliases, layer_aliases,
                         inferred_commands):
    words = os.environ['COMP_LINE'].split()
    command_name = words[1]
    prefix, _ = _split_prefix(command_name)

    choices = [(prefix + x) for x in command_map.keys()]
    for key, val in command_aliases:
        choices.append(prefix + key)
    choices += [
        x + "." + y for x in layer_aliases.keys() for y in command_map.keys()
    ]
    choices += [x for x in inferred_commands.keys() if x not in choices]

    # TODO: if react. is already parsed, then also propose react.local._ and react.local.*
    # so that the prompt can get expanded to include the next layer
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


def _command_name(command_map, command_aliases, layer_aliases,
                  inferred_commands):
    if "_ARGCOMPLETE" in os.environ:
        return _handle_arg_complete(command_map, command_aliases,
                                    layer_aliases, inferred_commands)
    if len(sys.argv) >= 2:
        return sys.argv[1]
    return 'help'


def _add_matching_layer_aliases_to_argv(layer_aliases, inferred_layer):
    prefix_str, sys.argv[1] = _split_prefix(sys.argv[1])
    selected_aliases = [x for x in prefix_str.split('.') if x]
    if inferred_layer and inferred_layer not in selected_aliases:
        selected_aliases.append(inferred_layer)

    matching_layer_aliases = [
        layer_aliases[x] for x in selected_aliases if layer_aliases[x]
    ]
    aliased_layer_options = ["--layer=%s" % x for x in matching_layer_aliases]
    sys.argv = sys.argv[:2] + [x for x in aliased_layer_options if x
                               ] + sys.argv[2:]


def execute_from_command_line(argv):
    root_layer = load_config(['config.yaml'])
    layer_aliases = root_layer.get('ROOT', {}).get('layer_aliases', {})

    try:
        inferred_commands = get_inferred_commands(root_layer)
    except Exception as e:
        _handle_exception(e)

    if len(sys.argv) > 1:
        inferred_layer = inferred_commands.get(sys.argv[1], None)
        _add_matching_layer_aliases_to_argv(layer_aliases, inferred_layer)

    try:
        config = Dodo.get_config()
        command_map = get_command_map(get_command_dirs_from_config(config))
    except Exception as e:
        _handle_exception(e)

    command_aliases = get_command_aliases(config)
    command_name = _command_name(command_map, command_aliases, layer_aliases,
                                 inferred_commands)

    if command_name == '--version':
        print(get_version())
        sys.exit(0)

    command_alias = find_command_alias(command_name, command_aliases)
    if command_alias and command_alias[0] in command_map:
        command_name = command_alias[0]
        sys.argv = sys.argv[:1] + command_alias + sys.argv[2:]

    if ('--trace' in sys.argv):
        sys.stderr.write('%s\n' % [x for x in sys.argv if x != '--trace'])
        sys.exit(0)

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
