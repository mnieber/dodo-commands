import os
import sys
from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.dependencies import yaml_round_trip_load
from dodo_commands.dependencies.get import plumbum, semantic_version
from dodo_commands.framework import get_version
from dodo_commands.framework.config import Paths
from dodo_commands.framework.util import bordered

Version = semantic_version.Version
local = plumbum.local


def _args():
    parser = ArgumentParser(
        description="Compare configuration version to "
        "version in original project config file."
    )
    parser.add_argument(
        "--dodo",
        dest="check_dodo",
        action="store_true",
        help=(
            "Check that the installed dodo commands version satisfies the "
            "minimal dodo commands version in the dodo config "
            "(/ROOT/required_dodo_commands_version)"
        ),
    )
    parser.add_argument(
        "--config",
        dest="check_config",
        action="store_true",
        help=(
            "Check that the version field in the local dodo commands config "
            "(/ROOT/version) is up-to-date with the version in the shared "
            "dodo commands config."
        ),
    )
    args = Dodo.parse_args(parser)
    return args


def _get_root_config_field(config_filename, field_name):
    with open(config_filename) as f:
        config = yaml_round_trip_load(f.read())
    return config.get("ROOT", {}).get(field_name, "")


def _config_filename():
    return os.path.join(Paths().config_dir(), "config.yaml")


def check_dodo_commands_version():  # noqa
    required_version = _get_root_config_field(
        _config_filename(), "required_dodo_commands_version"
    )
    if required_version:
        actual_version = get_version()
        if Version(actual_version) < Version(required_version):
            sys.stdout.write(
                bordered(
                    'The dodo_commands package needs to be upgraded (%s < %s). Tip: use "dodo upgrade"'
                    % (
                        actual_version,
                        required_version,
                    ),
                )
            )
            sys.stdout.write("\n")


def check_config_changes():  # noqa
    if os.path.exists(os.path.join(Paths().config_dir(), ".git")):
        with local.cwd(Paths().config_dir()):
            changes = local["git"]("status", "--short")
            if changes:
                sys.stdout.write(
                    bordered(
                        'Configuration has changes (tip: use "dodo commit-config"):\n'
                        + changes
                    )
                )
                sys.stdout.write("\n")


if Dodo.is_main(__name__, safe=False):
    args = _args()
    if args.check_dodo:
        check_dodo_commands_version()
    if args.check_config:
        check_config_changes()
