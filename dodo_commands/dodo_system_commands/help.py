from collections import defaultdict
import os
import sys
import ruamel.yaml
from argparse import ArgumentParser

from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.config import build_config
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.version import get_version
from dodo_commands.framework.funcy import drill, map_with, keep_if
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


def _collect_command_dirs(config, config_io, command_dir_2_alias_set,
                          command_aliases, target_path_by_alias,
                          layer_by_alias_target_path):
    config_memo = ruamel.yaml.round_trip_dump(config)

    for alias, target_path in target_path_by_alias.items():

        def has_command_path(layer):
            return drill(layer, 'ROOT', 'command_path', default=None)

        layer_filenames = layer_filename_superset([target_path],
                                                  config_io=config_io)
        extra_layers = map_with(config_io.load)(layer_filenames)
        if keep_if(has_command_path)(extra_layers):
            base_config = ruamel.yaml.round_trip_load(config_memo)
            updated_config = build_config([base_config] + extra_layers)
            for command_dir in get_command_dirs_from_config(updated_config):
                alias_set = command_dir_2_alias_set[command_dir]
                _add_to_alias_set(alias_set, alias)

        layer = layer_by_alias_target_path[target_path]
        for command_alias in layer.get('ROOT', {}).get('aliases', {}).items():
            inferred_commands = drill(layer,
                                      'ROOT',
                                      'inferred_commands',
                                      default=[])
            prefix = ("" if command_alias[0] in inferred_commands else
                      (alias + "."))

            postfix = " --layer=%s" % target_path
            command_aliases[prefix +
                            command_alias[0]] = command_alias[1] + postfix


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
    for alias, target_path in sorted(layer_aliases.items()):
        sys.stdout.write("%s = %s\n" % (alias.ljust(col_width), target_path))


def _print_command_aliases(command_aliases, inferred_commands, layer_aliases):
    col_width = max(len(x) for x in command_aliases.keys())

    sys.stdout.write("Command aliases:\n\n")
    for alias, target_path in sorted(command_aliases.items()):
        sys.stdout.write("%s = %s\n" % (alias.ljust(col_width), target_path))


def _add_to_alias_set(alias_set, alias):
    if '' in alias_set:
        return
    alias_set.add(alias)


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.command:
        Dodo.run([sys.argv[0], args.command, '--help'])
    else:
        ctr = Dodo.get_container()

        command_dirs = ctr.commands.command_dirs

        command_dir_2_alias_set = defaultdict(lambda: set())
        for command_dir in command_dirs:
            alias_set = command_dir_2_alias_set[command_dir]
            _add_to_alias_set(alias_set, '')

        command_aliases = dict(ctr.commands.aliases)
        _collect_command_dirs(ctr.config.config, ctr.layers.config_io,
                              command_dir_2_alias_set, command_aliases,
                              ctr.layers.target_path_by_alias,
                              ctr.layers.layer_by_alias_target_path)

        alias_set_2_command_dirs = defaultdict(lambda: list())
        for command_dir, alias_set in command_dir_2_alias_set.items():
            alias_set_2_command_dirs[tuple(alias_set)].append(command_dir)

        _print_command_dirs(args, alias_set_2_command_dirs,
                            ctr.commands.layer_alias_by_inferred_command)

        if not args.commands:
            layer_aliases = dict(ctr.layers.target_path_by_alias)
            if layer_aliases:
                _print_layer_aliases(layer_aliases)
            sys.stdout.write('\n')
            _print_command_aliases(
                command_aliases, ctr.commands.layer_alias_by_inferred_command,
                layer_aliases)
            sys.stdout.write('\n')
