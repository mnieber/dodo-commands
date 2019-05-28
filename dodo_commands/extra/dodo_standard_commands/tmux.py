from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
import sys
from six.moves import input as raw_input
from dodo_commands.framework.util import filter_choices
from plumbum.cmd import tmux

session_id = os.path.expandvars('$USER')


def _args():
    parser = ArgumentParser()
    parser.add_argument('--kill-session', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--run', type=int, nargs='?', const=-1)
    args = Dodo.parse_args(parser)
    args.command_map = Dodo.get_config('/TMUX/commands', [])
    return args


def _create_tmux_window():
    # Create tmux session
    Dodo.run(['tmux', '-2', 'new-session', '-d', '-s', session_id], )

    # Create a tmux window
    Dodo.run(['tmux', 'new-window', '-t', '%s:1' % session_id, '-n', 'Logs'], )


def _get_commands_and_labels(command_map):
    label_size = 0
    for label in command_map:
        label_size = max(label_size, len(label))
    label_prefix = "%0" + str(label_size) + "s"

    commands, labels = [], []
    for label in command_map:
        for command in command_map[label]:
            commands.append(command)
            format_string = "%02s [" + label_prefix + "] - %s"
            labels.append(format_string % (str(len(commands)), label, command))

    return commands, labels


def _get_selected_commands(commands, labels):
    print()
    for label in labels:
        print(label)

    raw_choice = raw_input(
        '\nSelect one or more commands (e.g. 1,3-4), or type a command: ')
    selected_commands, span = filter_choices(commands, raw_choice)
    if span != [0, len(raw_choice)]:
        selected_commands = [raw_choice]
    return selected_commands


if Dodo.is_main(__name__):
    args = _args()
    check_exists = Dodo.get_config('/TMUX/check_exists', '/')
    if not os.path.exists(check_exists):
        raise CommandError("Path %s does not exist" % check_exists)

    commands, labels = _get_commands_and_labels(args.command_map)

    if args.list:
        print()
        for label in labels:
            print(label)
        sys.exit(0)

    if args.run:
        selected_commands = (_get_selected_commands(commands, labels)
                             if args.run == -1 else [commands[args.run - 1]])
        for command in selected_commands:
            Dodo.run(['bash', '-c', command])
        sys.exit(0)

    has_session = False
    try:
        sessions = tmux('ls')
        for session in sessions.split('\n'):
            has_session = has_session or session.startswith('%s:' % session_id)
    except:
        pass

    if has_session and args.kill_session:
        Dodo.run(['tmux', 'kill-session', '-t', session_id], )

    if not has_session:
        _create_tmux_window()
        Dodo.run(['tmux', 'send-keys', 'dodo tmux', 'C-m'], )
        # Attach to tmux session
        Dodo.run(['tmux', '-2', 'attach-session', '-t', session_id], )
    else:
        while True:
            selected_commands = _get_selected_commands(commands, labels)
            for command in selected_commands:
                Dodo.run(['tmux', 'split-window', '-v'], )
                Dodo.run(['tmux', 'send-keys', command, 'C-m'], )

            # Set default window
            tmux('select-pane', '-t', '0')
            tmux('select-layout', 'tile')
