from collections import defaultdict
import os
import sys
from argparse import ArgumentParser

from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.config import load_config
from dodo_commands.framework import get_version
from dodo_commands.framework.inferred_commands import get_inferred_commands
from dodo_commands.framework.alias import get_command_aliases
from dodo_commands import Dodo


def _args():
    parser = ArgumentParser(description='Show help on a command')
    parser.add_argument('command', nargs='*')
    parser.add_argument('--commands', action='store_true')
    args = Dodo.parse_args(parser)
    return args


def _header_section():
    prog_name = os.path.basename(sys.argv[0])

    lines = [
        "",
        "Version %s (%s --version)." % (get_version(), prog_name),
        "To get help on a specific command, run it with the --help flag.",
        "Available commands (dodo help --commands):\n\n",
    ]
    return '\n'.join(lines)


def _commands_section(command_map, inferred_commands, use_columns=True):
    def format_name(command_name):
        inferred_layer = inferred_commands.get(command_name, None)
        return ("%s (%s)" % (command_name, inferred_layer)
                if inferred_layer else command_name)

    """Return the script's main help text, as a string."""
    if not use_columns:
        lines = [x for x in sorted(command_map.keys())]
    else:
        lines = []

        max_name_size = -1
        command_groups = defaultdict(lambda: [])
        for command_name, command_map_item in sorted(command_map.items()):
            formatted_name = format_name(command_name)
            max_name_size = max(max_name_size, len(formatted_name))
            command_groups[command_map_item.group].append(formatted_name)

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
            lines.append("".join(name.ljust(col_width) for name in names))

    return '\n'.join(lines)


def _layer_aliases(config):
    root_node = config.get('ROOT', [])
    return root_node.get('layer_aliases', {}).items()


def _collect_command_dirs(config, layer_filenames, command_dir_2_alias_set,
                          command_aliases):
    config_io = Dodo.get_config_io()
    for alias, alias_target in _layer_aliases(config):
        extra_layer_filenames = [
            x for x in config_io.glob([alias_target])
            if x not in layer_filenames
        ]
        updated_layer = load_config(layer_filenames + extra_layer_filenames,
                                    warn=False)
        for command_dir in get_command_dirs_from_config(updated_layer):
            alias_set = command_dir_2_alias_set[command_dir]
            _add_to_alias_set(alias_set, alias)

        for command_alias in get_command_aliases(updated_layer):
            command_aliases[command_alias[0]] = command_alias[1]


def _print_command_dirs(args, alias_set_2_command_dirs, inferred_commands):
    if not args.commands:
        sys.stdout.write(_header_section())

    root_set = ('', )
    command_map = get_command_map(alias_set_2_command_dirs[root_set])
    sys.stdout.write(
        _commands_section(
            command_map, inferred_commands, use_columns=not args.commands) +
        '\n')

    for alias_set, command_dirs in alias_set_2_command_dirs.items():
        if alias_set == root_set:
            continue

        sys.stdout.write("\nCommands for layer alias(es): %s\n\n" %
                         ", ".join(alias_set))
        command_map = get_command_map(command_dirs)
        sys.stdout.write(
            _commands_section(command_map,
                              inferred_commands,
                              use_columns=not args.commands) + '\n')


def _print_layer_aliases(layer_aliases):
    col_width = max(len(x) for x in layer_aliases.keys())

    sys.stdout.write("Layer aliases:\n\n")
    for alias, alias_target in sorted(layer_aliases.items()):
        sys.stdout.write("%s = %s\n" % (alias.ljust(col_width), alias_target))


def _print_command_aliases(command_aliases, inferred_commands, layer_aliases):
    col_width = max(len(x) for x in command_aliases.keys())

    sys.stdout.write("Command aliases:\n\n")
    for alias, alias_target in sorted(command_aliases.items()):
        inferred_layer = inferred_commands[alias]
        postfix = " --layer=%s" % layer_aliases[
            inferred_layer] if inferred_layer in layer_aliases else ""
        sys.stdout.write("%s = %s%s\n" %
                         (alias.ljust(col_width), alias_target, postfix))


def _add_to_alias_set(alias_set, alias):
    if '' in alias_set:
        return
    alias_set.add(alias)


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.command:
        Dodo.run([sys.argv[0], args.command, '--help'])
    else:
        command_dirs = get_command_dirs_from_config(Dodo.get_config())

        command_dir_2_alias_set = defaultdict(lambda: set())
        for command_dir in command_dirs:
            alias_set = command_dir_2_alias_set[command_dir]
            _add_to_alias_set(alias_set, '')

        command_aliases = {}
        _collect_command_dirs(Dodo.get_config(), Dodo._layer_filenames,
                              command_dir_2_alias_set, command_aliases)

        alias_set_2_command_dirs = defaultdict(lambda: list())
        for command_dir, alias_set in command_dir_2_alias_set.items():
            alias_set_2_command_dirs[tuple(alias_set)].append(command_dir)

        inferred_commands = get_inferred_commands(Dodo.get_config())
        _print_command_dirs(args, alias_set_2_command_dirs, inferred_commands)

        if not args.commands:
            layer_aliases = dict(_layer_aliases(Dodo.get_config()))
            _print_layer_aliases(layer_aliases)
            sys.stdout.write('\n')
            _print_command_aliases(command_aliases, inferred_commands,
                                   layer_aliases)
            sys.stdout.write('\n')
