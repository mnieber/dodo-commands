import glob
import os
import sys
from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.decorator_utils import _all_decorators
from dodo_commands.framework.paths import Paths


def _args():  # noqa
    parser = ArgumentParser(
        description=(
            "Print the value of /ROOT/<what>_dir. For example: "
            + '"dodo which src" prints the value of /ROOT/src_dir.'
        )
    )
    parser.add_argument(
        "what",
        nargs="?",
    )
    parser.add_argument(
        "--cd", action="store_true", help="Prefix the output with 'cd '"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--config", action="store_true", help="Print where the config file is"
    )
    group.add_argument(
        "--global-config",
        action="store_true",
        help="Print where the global config file is",
    )
    group.add_argument(
        "--env-dir",
        action="store_true",
        help="Print where the environment directory is",
    )
    group.add_argument(
        "--project-dir",
        action="store_true",
        help="Print where the project directory is",
    )
    group.add_argument(
        "--config-dir", action="store_true", help="Print where the config directory is"
    )
    group.add_argument(
        "--python-env-dir",
        action="store_true",
        help="Print where the python virtual env directory is",
    )
    group.add_argument(
        "--script", help="Print where the dodo command script with given name is"
    )
    group.add_argument(
        "--decorators",
        action="store_true",
        help="Prints which command decorators are available",
    )
    group.add_argument(
        "--envs", action="store_true", help="Prints which environments are available"
    )
    group.add_argument(
        "--env", action="store_true", help="Prints name of the active environment"
    )
    group.add_argument(
        "--layers", action="store_true", help="Prints which layers are active"
    )
    group.add_argument(
        "--default-commands",
        action="store_true",
        help="Prints the directory where default commands are stored",
    )
    group.add_argument(
        "--global-commands",
        action="store_true",
        help="Prints the directory where global commands are stored",
    )
    group.add_argument(
        "--fish-config",
        action="store_true",
        help="Prints the location of the additional fish config files",
    )

    return Dodo.parse_args(parser)


def _which_script(script):
    command_dirs = get_command_dirs_from_config(Dodo.get())
    for item in command_dirs:
        script_path = os.path.join(item, script + ".py")
        if os.path.exists(script_path):
            return os.path.realpath(script_path)

    for item in command_dirs:
        for fn in glob.glob(os.path.join(item, "dodo.*.sh")):
            return os.path.realpath(fn)

    return None


def _which_dir(directory):
    return Dodo.get("/ROOT/%s_dir" % directory, None)


if Dodo.is_main(__name__):
    args = _args()

    def report(x):
        prefix = "cd " if args.cd else ""
        sys.stdout.write("%s%s" % (prefix, x))

    if args.config:
        if os.path.exists(Paths().config_dir()):
            report(os.path.join(Paths().config_dir(), "config.yaml"))
    elif args.global_config:
        report(Paths().global_config_filename() + "\n")
    elif args.global_commands:
        report(Paths().global_commands_dir() + "\n")
    elif args.default_commands:
        report(Paths().default_commands_dir() + "\n")
    elif args.script:
        report(_which_script(args.script) + "\n")
    elif args.env_dir:
        report(Paths().env_dir() + "\n")
    elif args.project_dir:
        report(_which_dir("project") + "\n")
    elif args.config_dir:
        report(_which_dir("config") + "\n")
    elif args.python_env_dir:
        python_env_dir = os.path.realpath(
            os.path.join(Paths().env_dir(), "python_env_dir")
        )
        if os.path.exists(python_env_dir):
            report(python_env_dir + "\n")
    elif args.decorators:
        report(", ".join(sorted(_all_decorators(Dodo.get()).keys())) + "\n")
    elif args.envs:
        report("\n".join(sorted(os.listdir(Paths().envs_dir()))) + "\n")
    elif args.env:
        if Dodo.get("/ROOT/env_name", None):
            report(Dodo.get("/ROOT/env_name") + "\n")
    elif args.layers:
        layer_paths = Dodo.get_container().layers.get_ordered_layer_paths()
        for layer_path in layer_paths:
            report(layer_path + "\n")
    elif args.what:
        x = _which_script(args.what) or _which_dir(args.what)
        if x:
            report(x + "\n")
    elif args.fish_config:
        report(os.path.realpath(os.path.join(Paths().extra_dir(), "dodo_fish")) + "\n")
    else:
        if Dodo.get("/ROOT/env_name", None):
            report(Dodo.get("/ROOT/env_name") + "\n")
