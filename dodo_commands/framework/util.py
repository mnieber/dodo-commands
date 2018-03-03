# -*- coding: utf-8 -*-

"""Utilities."""
from six.moves import input as raw_input
import os
import sys


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


_global_config = """
[DodoCommands]
projects_dir=~/projects
python_interpreter=python
diff_tool=diff
pretty_print=true
"""


def create_global_config():
    """Create config file and default_commands dir."""
    base_dir = os.path.expanduser('~/.dodo_commands')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    config_filename = os.path.join(base_dir, "config")
    if not os.path.exists(config_filename):
        with open(config_filename, 'w') as f:
            f.write(_global_config)

    default_commands_dir = os.path.join(base_dir, "default_commands")
    if not os.path.exists(default_commands_dir):
        os.mkdir(default_commands_dir)

    init_py = os.path.join(default_commands_dir, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, 'w') as f:
            pass


def remove_trailing_dashes(args):
    """Removes first -- item from args."""
    return args[1:] if args[:1] == ['--'] else args


def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)


def is_using_system_dodo():
    import dodo_commands
    dodo_commands_path = dodo_commands.__path__[0]
    return os.path.realpath(dodo_commands_path) == dodo_commands_path
