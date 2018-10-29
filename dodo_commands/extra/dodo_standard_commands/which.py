from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.config import (CommandPath,
                                            load_global_config_parser)
import os
import sys


def _args():  # noqa
    parser = ArgumentParser(
        description=('Print the value of /ROOT/<what>_dir. For example: ' +
                     '"dodo which src" prints the value of /ROOT/src_dir.'))
    parser.add_argument(
        'what',
        nargs='?', )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--config', action="store_true", help='Print where the config file is')
    group.add_argument(
        '--global-config',
        action="store_true",
        help='Print where the global config file is')
    group.add_argument(
        '--script',
        help='Print where the dodo command script with given name is')
    group.add_argument(
        '--dir',
        dest='directory',
        help='Finds the X_dir value in the configuration, where X is the given option value'
    )
    group.add_argument(
        '--decorators',
        action="store_true",
        help='Prints which command decorators are available')
    group.add_argument(
        '--projects',
        action="store_true",
        help='Prints which projects are available')
    group.add_argument(
        '--default-commands',
        action="store_true",
        help='Prints the directory where default commands are stored')

    return Dodo.parse_args(parser)


def _which_script(script):
    command_path = CommandPath(Dodo.config)
    for item in command_path.items:
        script_path = os.path.join(item, script + ".py")
        if os.path.exists(script_path):
            return script_path
    return None


def _which_dir(directory):
    return Dodo.get_config("/ROOT/%s_dir" % directory, None)


def _projects_dir():
    return os.path.expanduser(load_global_config_parser().get("settings",
                                                              "projects_dir"))


if Dodo.is_main(__name__):
    args = _args()

    if args.config:
        print(os.path.join(Paths().res_dir(), "config.yaml"))
    elif args.global_config:
        sys.stdout.write(Paths().global_config_filename() + '\n')
    elif args.default_commands:
        sys.stdout.write(Paths().default_commands_dir() + '\n')
    elif args.script:
        sys.stdout.write(_which_script(args.script) + '\n')
    elif args.directory:
        sys.stdout.write(_which_dir(args.directory) + '\n')
    elif args.decorators:
        sys.stdout.write(", ".join(sorted(Dodo.all_decorators().keys())) +
                         '\n')
    elif args.projects:
        projects = [
            x for x in os.listdir(_projects_dir())
            if os.path.isdir(
                os.path.join(_projects_dir(), x, "dodo_commands", "res"))
        ]
        sys.stdout.write('\n'.join(sorted(projects)) + '\n')
    elif args.what:
        x = _which_script(args.what) or _which_dir(args.what)
        if x:
            sys.stdout.write(x + '\n')
    else:
        sys.stdout.write(Dodo.get_config("/ROOT/project_name") + '\n')
