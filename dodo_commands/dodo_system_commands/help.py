import os
import sys
from argparse import ArgumentParser
from collections import defaultdict

from dodo_commands import Dodo
from dodo_commands.dependencies import (yaml_round_trip_dump,
                                        yaml_round_trip_load)
from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.config import build_config
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.funcy import drill, keep_if, map_with
from dodo_commands.framework.version import get_version


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


def _collect_command_dirs(config, config_io, layer_names_by_command_dir,
                          command_aliases, layer_props_by_layer_name,
                          layer_by_target_path):
    config_memo = yaml_round_trip_dump(config)

    for layer_name, layer_props in layer_props_by_layer_name.items():

        def has_command_path(layer):
            return drill(layer, 'ROOT', 'command_path', default=None)

        layer_filenames = layer_filename_superset([layer_props.target_path],
                                                  config_io=config_io)
        extra_layers = map_with(config_io.load)(layer_filenames)
        if keep_if(has_command_path)(extra_layers):
            base_config = yaml_round_trip_load(config_memo)
            updated_config = build_config([base_config] + extra_layers)
            for command_dir in get_command_dirs_from_config(updated_config):
                layer_names = layer_names_by_command_dir[command_dir]
                _add_to_layer_names(layer_names, layer_name)

        layer = layer_by_target_path[layer_props.target_path]
        for command_alias in layer.get('ROOT', {}).get('aliases', {}).items():
            alias_prefix = (
                "" if command_alias[0] in layer_props.inferred_commands else
                (layer_name + "."))
            cmd_prefix = layer_name + "."
            command_aliases[alias_prefix +
                            command_alias[0]] = cmd_prefix + command_alias[1]


def _print_command_dirs(args, layer_names_2_command_dirs, inferred_commands):
    if not args.commands:
        sys.stdout.write(_header_section())

    root_set = ('', )
    command_map = get_command_map(layer_names_2_command_dirs[root_set])
    sys.stdout.write(
        _commands_section(
            command_map, inferred_commands, use_columns=not args.commands) +
        '\n')

    for layer_names, command_dirs in layer_names_2_command_dirs.items():
        if layer_names == root_set:
            continue

        sys.stdout.write("\nCommands for layer(s): %s\n\n" %
                         ", ".join(layer_names))
        command_map = get_command_map(command_dirs)
        sys.stdout.write(
            _commands_section(command_map,
                              inferred_commands,
                              use_columns=not args.commands) + '\n')


def _print_layer_names(layer_props_by_layer_name):
    layer_names = layer_props_by_layer_name.keys()
    col_width = max(len(x) for x in layer_names)

    sys.stdout.write("Layers:\n\n")
    for layer_name, layer_props in sorted(layer_props_by_layer_name.items()):
        sys.stdout.write(
            "%s = %s\n" %
            (layer_name.ljust(col_width), layer_props.target_path))


def _print_command_aliases(command_aliases, inferred_commands):
    if command_aliases:
        col_width = max(len(x) for x in command_aliases.keys())

        sys.stdout.write("Command aliases:\n\n")
        for alias, target_path in sorted(command_aliases.items()):
            sys.stdout.write("%s = %s\n" %
                             (alias.ljust(col_width), target_path))


def _add_to_layer_names(layer_names, layer_name):
    if '' in layer_names:
        return
    layer_names.add(layer_name)


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.command:
        Dodo.run([sys.argv[0], args.command, '--help'])
    else:
        ctr = Dodo.get_container()

        command_dirs = ctr.commands.command_dirs

        layer_names_by_command_dir = defaultdict(lambda: set())
        for command_dir in command_dirs:
            layer_names = layer_names_by_command_dir[command_dir]
            _add_to_layer_names(layer_names, '')

        command_aliases = dict(ctr.commands.aliases)
        _collect_command_dirs(ctr.config.config, ctr.layers.config_io,
                              layer_names_by_command_dir, command_aliases,
                              ctr.layers.layer_props_by_layer_name,
                              ctr.layers.layer_by_target_path)

        layer_names_2_command_dirs = defaultdict(lambda: list())
        for command_dir, layer_names in layer_names_by_command_dir.items():
            layer_names_2_command_dirs[tuple(layer_names)].append(command_dir)

        _print_command_dirs(args, layer_names_2_command_dirs,
                            ctr.commands.layer_name_by_inferred_command)

        if not args.commands:
            if ctr.layers.layer_props_by_layer_name:
                _print_layer_names(dict(ctr.layers.layer_props_by_layer_name))
            sys.stdout.write('\n')
            _print_command_aliases(command_aliases,
                                   ctr.commands.layer_name_by_inferred_command)
            sys.stdout.write('\n')
