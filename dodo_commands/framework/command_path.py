import glob
import hashlib
import json
import os
import sys

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import symlink


def _glob_command_dirs(patterns):
    result = []
    for pattern in patterns:
        for x in glob.glob(os.path.expanduser(pattern)):
            if os.path.isdir(x) and not os.path.basename(x).startswith("_"):
                result.append(x)
    return result


def get_command_dirs(include_patterns, exclude_patterns):
    excluded_command_dirs = _glob_command_dirs(exclude_patterns)

    items = sorted(
        [
            x
            for x in _glob_command_dirs(include_patterns)
            if x not in excluded_command_dirs
        ]
    )

    basenames = [os.path.basename(x) for x in items]
    for basename in basenames:
        if basenames.count(basename) > 1:
            raise CommandError("More than 1 command path with name %s" % basename)
    return items


def _create_search_path_dir(command_dirs):
    hash_code = hashlib.md5(json.dumps(command_dirs).encode("utf-8")).hexdigest()
    search_path_dir = os.path.join(
        Paths().global_config_dir(), "search_path", hash_code
    )

    if not os.path.exists(search_path_dir):
        os.makedirs(search_path_dir)
        open(os.path.join(search_path_dir, "__init__.py"), "a").close()
        for command_dir in command_dirs:
            basename = os.path.basename(command_dir)
            path = os.path.join(search_path_dir, basename)
            if not os.path.exists(path):
                symlink(command_dir, path)

    return search_path_dir


def extend_sys_path(command_dirs):
    search_path_dir = _create_search_path_dir(command_dirs)
    if search_path_dir not in sys.path:
        sys.path.append(search_path_dir)


def get_command_dirs_from_config(config):
    root_config = config.get("ROOT", {})
    command_path = root_config.get("command_path", [])
    command_path_exclude = root_config.get("command_path_exclude", [])
    return get_command_dirs(
        include_patterns=command_path, exclude_patterns=command_path_exclude
    )
