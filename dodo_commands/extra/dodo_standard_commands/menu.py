from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
import sys
from six.moves import input as raw_input
from dodo_commands.framework.util import (filter_choices, exe_exists,
                                          InvalidIndex)
from plumbum.cmd import tmux


def _session_id(category):
    return os.path.expandvars('$USER') + "_" + category


def _normalize(category):
    return category.replace(' ', '-')


def _args():
    command_map = Dodo.get_config('/MENU/commands', {})

    parser = ArgumentParser()
    parser.add_argument('category',
                        choices=['all'] +
                        list([_normalize(x) for x in command_map.keys()]),
                        nargs='?')
    parser.add_argument('--tmux', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--run', type=int, nargs='?', const=-1)

    args = Dodo.parse_args(parser)
    args.category = args.category or 'all'
    args.run = -1 if args.run is None else args.run
    args.command_map = command_map

    return args


def _create_tmux_window(session_id):
    # Create tmux session
    Dodo.run(['tmux', '-2', 'new-session', '-d', '-s', session_id], )

    # Create a tmux window
    Dodo.run(['tmux', 'new-window', '-t', '%s:1' % session_id, '-n', 'Logs'], )


def _get_categories(command_map, category):
    return [
        x for x in command_map
        if category == 'all' or _normalize(x) == category
    ]


def _get_commands_and_labels(command_map, category):
    categories = _get_categories(command_map, category)
    label_size = 0
    for category in categories:
        label_size = max(label_size, len(category))
    label_prefix = "%0" + str(label_size) + "s"

    commands, labels = [], []
    for category in categories:
        for command in command_map[category]:
            commands.append(command)
            format_string = "%02s [" + label_prefix + "] - %s"
            labels.append(format_string %
                          (str(len(commands)), category, command))

    return commands, labels


def _get_selected_commands(commands, labels, allow_free_text=False):
    print()
    for label in labels:
        print(label)

    while True:
        raw_choice = raw_input(
            '\nSelect one or more commands (e.g. 1,3-4)%s or type 0 to exit: '
            % (', or type a command,' if allow_free_text else ''))
        selected_commands, span = filter_choices(commands, raw_choice)
        if span == [0, len(raw_choice)]:
            return selected_commands
        elif allow_free_text:
            return [raw_choice]
        else:
            print("Sorry, I could not parse that.")


if Dodo.is_main(__name__):
    args = _args()
    check_exists = Dodo.get_config('/MENU/check_exists', '/')
    if not os.path.exists(check_exists):
        raise CommandError("Path %s does not exist" % check_exists)

    commands, labels = _get_commands_and_labels(args.command_map,
                                                args.category)

    if not commands:
        raise CommandError(
            "No commands were found in the /MENU configuration key")

    if args.list:
        print()
        for label in labels:
            print(label)
    elif args.tmux:
        if not exe_exists('tmux'):
            raise CommandError('Tmux is not installed on this sytem.')

        session_id = _session_id(args.category)
        has_session = False
        try:
            sessions = tmux('ls')
            for session in sessions.split('\n'):
                has_session = has_session or session.startswith(
                    '%s:' % session_id)
        except:
            pass

        if not has_session:
            _create_tmux_window(session_id)
            Dodo.run([
                'tmux', 'send-keys',
                'dodo menu --tmux %s' % args.category, 'C-m'
            ], )
            # Attach to tmux session
            Dodo.run(['tmux', '-2', 'attach-session', '-t', session_id], )
        else:
            while True:
                try:
                    selected_commands = _get_selected_commands(
                        commands, labels, allow_free_text=True)
                except InvalidIndex as e:
                    if e.index == -1:
                        sys.exit(0)
                    raise
                for command in selected_commands:
                    Dodo.run(['tmux', 'split-window', '-v'], )
                    Dodo.run(['tmux', 'send-keys', command, 'C-m'], )

                # Set default window
                tmux('select-pane', '-t', '0')
                tmux('select-layout', 'tile')
    else:
        try:
            selected_commands = (_get_selected_commands(commands, labels) if
                                 args.run == -1 else [commands[args.run - 1]])
        except InvalidIndex as e:
            if e.index == -1:
                sys.exit(0)
            raise
        for command in selected_commands:
            Dodo.run(['bash', '-c', command])
