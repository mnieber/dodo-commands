from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.config import (get_command_path, Paths,
                                            projects_dir, ConfigLoader)
import glob
import os
import ruamel.yaml
import sys


def _args():  # noqa
    parser = ArgumentParser(
        description=('Print the value of /ROOT/<what>_dir. For example: ' +
                     '"dodo which src" prints the value of /ROOT/src_dir.'))
    parser.add_argument(
        'what',
        nargs='?',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config',
                       action="store_true",
                       help='Print where the config file is')
    group.add_argument('--global-config',
                       action="store_true",
                       help='Print where the global config file is')
    group.add_argument(
        '--script',
        help='Print where the dodo command script with given name is')
    group.add_argument(
        '--dir',
        dest='directory',
        help=
        'Finds the X_dir value in the configuration, where X is the given option value'
    )
    group.add_argument('--decorators',
                       action="store_true",
                       help='Prints which command decorators are available')
    group.add_argument('--projects',
                       action="store_true",
                       help='Prints which projects are available')
    group.add_argument('--project',
                       action="store_true",
                       help='Prints name of the active project')
    group.add_argument('--layers',
                       action="store_true",
                       help='Prints which layers are active')
    group.add_argument(
        '--default-commands',
        action="store_true",
        help='Prints the directory where default commands are stored')
    group.add_argument(
        '--global-commands',
        action="store_true",
        help='Prints the directory where global commands are stored')

    return Dodo.parse_args(parser)


def _which_script(script):
    command_path = get_command_path(Dodo.get_config())
    for item in command_path.items:
        script_path = os.path.join(item, script + ".py")
        if os.path.exists(script_path):
            return os.path.realpath(script_path)

    for item in command_path.items:
        for yml in glob.glob(os.path.join(item, "dodo.*.yaml")):
            with open(yml) as ifs:
                if script in ruamel.yaml.round_trip_load(ifs.read()).keys():
                    return os.path.realpath(yml)

    return None


def _which_dir(directory):
    return Dodo.get_config("/ROOT/%s_dir" % directory, None)


if Dodo.is_main(__name__):
    args = _args()

    if args.config:
        if os.path.exists(Paths().project_dir()):
            print(os.path.join(Paths().res_dir(), "config.yaml"))
    elif args.global_config:
        sys.stdout.write(Paths().global_config_filename() + '\n')
    elif args.global_commands:
        sys.stdout.write(Paths().global_commands_dir() + '\n')
    elif args.default_commands:
        sys.stdout.write(Paths().default_commands_dir() + '\n')
    elif args.script:
        sys.stdout.write(_which_script(args.script) + '\n')
    elif args.directory:
        sys.stdout.write(_which_dir(args.directory) + '\n')
    elif args.decorators:
        sys.stdout.write(", ".join(sorted(Dodo._all_decorators().keys())) +
                         '\n')
    elif args.projects:
        projects = [
            x for x in os.listdir(projects_dir()) if os.path.isdir(
                os.path.join(projects_dir(), x, "dodo_commands", "res"))
        ] if os.path.exists(projects_dir()) else []
        sys.stdout.write('\n'.join(sorted(projects)) + '\n')
    elif args.project:
        if Dodo.get_config("/ROOT/project_name", None):
            sys.stdout.write(Dodo.get_config("/ROOT/project_name") + '\n')
    elif args.layers:
        for layer_filename in ConfigLoader().get_layers(Dodo.get_config()):
            sys.stdout.write(layer_filename + '\n')
    elif args.what:
        x = _which_script(args.what) or _which_dir(args.what)
        if x:
            sys.stdout.write(x + '\n')
    else:
        if Dodo.get_config("/ROOT/project_name", None):
            sys.stdout.write(Dodo.get_config("/ROOT/project_name") + '\n')
