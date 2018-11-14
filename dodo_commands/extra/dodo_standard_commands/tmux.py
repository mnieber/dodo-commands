from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
from six.moves import input as raw_input
from dodo_commands.framework.util import filter_choices
from plumbum.cmd import tmux

session_id = os.path.expandvars('$USER')


def _args():
    parser = ArgumentParser()
    parser.add_argument('--kill-session', action='store_true')
    args = Dodo.parse_args(parser)
    args.commands = Dodo.get_config('/TMUX/commands', [])
    return args


def _create_tmux_window():
    # Create tmux session
    Dodo.run(['tmux', '-2', 'new-session', '-d', '-s', session_id], )

    # Create a tmux window
    Dodo.run(['tmux', 'new-window', '-t', '%s:1' % session_id, '-n', 'Logs'], )


if Dodo.is_main(__name__):
    args = _args()
    check_exists = Dodo.get_config('/TMUX/check_exists', '/')
    if not os.path.exists(check_exists):
        raise CommandError("Path %s does not exist" % check_exists)

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
            commands = []
            label_size = 0
            for label in args.commands:
                label_size = max(label_size, len(label))
            label_prefix = "%0" + str(label_size) + "s"

            print()
            for label in args.commands:
                for command in args.commands[label]:
                    commands.append(command)
                    format_string = "%02s [" + label_prefix + "] - %s"
                    print(format_string % (str(len(commands)), label, command))

            raw_choice = raw_input(
                '\nSelect one or more commands (e.g. 1,3-4), or type a command: '
            )
            selected_commands, span = filter_choices(commands, raw_choice)
            if span != [0, len(raw_choice)]:
                selected_commands = [raw_choice]

            for idx, command in enumerate(selected_commands):
                Dodo.run(['tmux', 'split-window', '-v'], )
                Dodo.run(['tmux', 'send-keys', command, 'C-m'], )

            # Set default window
            tmux('select-pane', '-t', '0')
            tmux('select-layout', 'tile')
