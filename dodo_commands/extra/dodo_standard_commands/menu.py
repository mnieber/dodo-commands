import os
import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.choice_picker import ChoicePicker
from dodo_commands.framework.util import exe_exists

tmux = plumbum.cmd.tmux


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
    tmux('-2', 'new-session', '-d', '-s', session_id)

    # Create a tmux window
    tmux('new-window', '-t', '%s:1' % session_id, '-n', 'Logs')


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
    class Picker(ChoicePicker):
        def print_choices(self, choices):
            print()
            for idx, label in enumerate(choices):
                print(label)
            print()

        def question(self):
            return (
                'Select one or more commands (e.g. 1,3-4)%s or type 0 to exit: '
                % (', or type a command,' if allow_free_text else ''))

        def on_invalid_index(self, index):
            if index == 0:
                sys.exit(0)

    picker = Picker(commands, allow_free_text=allow_free_text, labels=labels)
    picker.pick()
    return [picker.free_text] if picker.free_text else picker.get_choices()


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
        except:  # noqa
            pass

        if not has_session:
            _create_tmux_window(session_id)
            tmux('send-keys', 'dodo menu --tmux %s' % args.category, 'C-m')
            # Attach to tmux session
            # HACK: why does this only work via Dodo.run?
            Dodo.run(['tmux', '-2', 'attach-session', '-t', session_id], )
        else:
            while True:
                selected_commands = _get_selected_commands(
                    commands, labels, allow_free_text=True)
                for command in selected_commands:
                    print(command)
                    tmux('split-window', '-v')
                    tmux('send-keys', command, 'C-m')

                # Set default window
                tmux('select-pane', '-t', '0')
                tmux('select-layout', 'tile')
    else:
        selected_commands = (_get_selected_commands(commands, labels)
                             if args.run == -1 else [commands[args.run - 1]])
        for command in selected_commands:
            Dodo.run(['bash', '-c', command])
