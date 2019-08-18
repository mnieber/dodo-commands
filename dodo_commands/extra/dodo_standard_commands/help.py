from collections import defaultdict
import os
import sys
from argparse import ArgumentParser

from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.command_path import get_command_path
from dodo_commands.framework import get_version
from dodo_commands import Dodo


def _args():
    parser = ArgumentParser(description='Show help on a command')
    parser.add_argument('command', nargs='*')
    parser.add_argument('--commands', action='store_true')
    args = Dodo.parse_args(parser)
    return args


def _main_help_text(command_map, commands_only=False):
    """Return the script's main help text, as a string."""
    prog_name = os.path.basename(sys.argv[0])

    if commands_only:
        usage = sorted(command_map.keys())
    else:
        usage = [
            "",
            "Version %s (%s --version)." % (get_version(), prog_name),
            "To get help on a specific command, run it with the --help flag.",
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


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.command:
        Dodo.run['']
    command_map = get_command_map(get_command_path(Dodo.get_config()))
    sys.stdout.write(
        _main_help_text(command_map, commands_only=args.commands) + '\n')
