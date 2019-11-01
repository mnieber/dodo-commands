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


def _get_selected_layer_alias_set():
    prefix_str, sys.argv[1] = _split_prefix(sys.argv[1])
    return set([x for x in prefix_str.split('.') if x])


def _get_layer_alias_targets(layer_aliases, selected_aliases):
    for x in selected_aliases:
        if x not in layer_aliases:
            raise CommandError("Unknown layer alias: %s" % x)
    return [layer_aliases[x] for x in selected_aliases]


def _add_layers_to_argv(layer_filenames):
    aliased_layer_options = ["--layer=%s" % x for x in layer_filenames]
    sys.argv = sys.argv[:2] + [
        x for x in aliased_layer_options if x and x not in sys.argv
    ] + sys.argv[2:]


def _process_layer_aliases(layer_aliases, inferred_commands):
    selected_aliases = _get_selected_layer_alias_set()

    inferred_layer = inferred_commands.get(sys.argv[1], None)
    if inferred_layer:
        selected_aliases.add(inferred_layer)

    layer_filenames = _get_layer_alias_targets(layer_aliases, selected_aliases)
    _add_layers_to_argv(layer_filenames)


def _process_command_alias(command_alias, layer_aliases, inferred_commands):
    # The command alias target may itself contain layer aliases and
    # inferred commands, so call _process_layer_aliases again
    sys.argv = sys.argv[:1] + command_alias + sys.argv[2:]
    _process_layer_aliases(layer_aliases, inferred_commands)
    command_name = sys.argv[1]
    return command_name


def execute_from_command_line(argv):
    root_layer = load_config(['config.yaml'], warn=False)
    layer_aliases = root_layer.get('ROOT', {}).get('layer_aliases', {})

    try:
        inferred_commands = get_inferred_commands(root_layer)
        if len(sys.argv) > 1:
            _process_layer_aliases(layer_aliases, inferred_commands)
    except Exception as e:
        _handle_exception(e)

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
    if command_alias:
        command_name = _process_command_alias(command_alias, layer_aliases,
                                              inferred_commands)

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
