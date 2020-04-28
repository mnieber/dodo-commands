import glob
import os
import sys
from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.dependencies import yaml_round_trip_load
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.container.utils import get_ordered_layer_paths
from dodo_commands.framework.decorator_utils import _all_decorators
from dodo_commands.framework.paths import Paths


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
    group.add_argument('--env-dir',
                       action="store_true",
                       help='Print where the environment directory is')
    group.add_argument('--project-dir',
                       action="store_true",
                       help='Print where the project directory is')
    group.add_argument('--config-dir',
                       action="store_true",
                       help='Print where the config directory is')
    group.add_argument('--python-env-dir',
                       action="store_true",
                       help='Print where the python virtual env directory is')
    group.add_argument(
        '--script',
        help='Print where the dodo command script with given name is')
    group.add_argument('--decorators',
                       action="store_true",
                       help='Prints which command decorators are available')
    group.add_argument('--envs',
                       action="store_true",
                       help='Prints which environments are available')
    group.add_argument('--env',
                       action="store_true",
                       help='Prints name of the active environment')
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
    command_dirs = get_command_dirs_from_config(Dodo.get())
    for item in command_dirs:
        script_path = os.path.join(item, script + ".py")
        if os.path.exists(script_path):
            return os.path.realpath(script_path)

    for item in command_dirs:
        for yml in glob.glob(os.path.join(item, "dodo.*.yaml")):
            with open(yml) as ifs:
                if script in yaml_round_trip_load(ifs.read()).keys():
                    return os.path.realpath(yml)

    return None


def _which_dir(directory):
    return Dodo.get("/ROOT/%s_dir" % directory, None)


if Dodo.is_main(__name__):
    args = _args()

    if args.config:
        if os.path.exists(Paths().config_dir()):
            print(os.path.join(Paths().config_dir(), "config.yaml"))
    elif args.global_config:
        sys.stdout.write(Paths().global_config_filename() + '\n')
    elif args.global_commands:
        sys.stdout.write(Paths().global_commands_dir() + '\n')
    elif args.default_commands:
        sys.stdout.write(Paths().default_commands_dir() + '\n')
    elif args.script:
        sys.stdout.write(_which_script(args.script) + '\n')
    elif args.env_dir:
        sys.stdout.write(Paths().env_dir())
    elif args.project_dir:
        sys.stdout.write(_which_dir("project") + '\n')
    elif args.config_dir:
        sys.stdout.write(_which_dir("config") + '\n')
    elif args.python_env_dir:
        python_env_dir = os.path.realpath(
            os.path.join(Paths().env_dir(), "python_env_dir"))
        if os.path.exists(python_env_dir):
            sys.stdout.write(python_env_dir + '\n')
    elif args.decorators:
        sys.stdout.write(
            ", ".join(sorted(_all_decorators(Dodo.get()).keys())) +
            '\n')
    elif args.envs:
        sys.stdout.write('\n'.join(sorted(os.listdir(Paths().envs_dir()))) +
                         '\n')
    elif args.env:
        if Dodo.get("/ROOT/env_name", None):
            sys.stdout.write(Dodo.get("/ROOT/env_name") + '\n')
    elif args.layers:
        layer_paths = get_ordered_layer_paths(Dodo.get_container())
        for layer_path in layer_paths:
            sys.stdout.write(layer_path + '\n')
    elif args.what:
        x = _which_script(args.what)
        if x:
            sys.stdout.write(x + '\n')
    else:
        if Dodo.get("/ROOT/env_name", None):
            sys.stdout.write(Dodo.get("/ROOT/env_name") + '\n')
