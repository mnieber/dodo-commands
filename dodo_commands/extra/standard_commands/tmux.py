from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
from six.moves import input as raw_input
from .dockerkill import _filter_choices
from plumbum.cmd import tmux


session_id = os.path.expandvars('$USER')


# # Kill previous session
# Dodo.runcmd(
#     ['tmux', 'kill-session', '-t', session_id],
# )


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.commands = Dodo.get_config('/TMUX/commands', [])
    return args


def _create_tmux_window():
    # Create tmux session
    Dodo.runcmd(
        ['tmux', '-2', 'new-session', '-d', '-s', session_id],
    )

    # Create a tmux window
    Dodo.runcmd(
        ['tmux', 'new-window', '-t', '%s:1' % session_id, '-n', 'Logs'],
    )


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

    if not has_session:
        _create_tmux_window()
        Dodo.runcmd(
            ['tmux', 'send-keys', 'dodo tmux', 'C-m'],
        )
        # Attach to tmux session
        Dodo.runcmd(
            ['tmux', '-2', 'attach-session', '-t', session_id],
        )
    else:
        while True:
            for idx, command in enumerate(args.commands):
                print("%d - %s" % (idx + 1, command))

            raw_choice = raw_input('Select one or more commands (e.g. 1,3-4), or type a command: ')
            selected_commands, span = _filter_choices(args.commands, raw_choice)
            if span != [0, len(raw_choice)]:
                selected_commands = [raw_choice]

            for idx, command in enumerate(selected_commands):
                Dodo.runcmd(
                    ['tmux', 'split-window', '-v'],
                )
                Dodo.runcmd(
                    ['tmux', 'send-keys', command, 'C-m'],
                )

            # Set default window
            tmux('select-pane', '-t', '0')
            tmux('select-layout', 'tile')
