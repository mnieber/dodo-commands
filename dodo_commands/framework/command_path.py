import glob
import hashlib
import json
import os
import sys

from dodo_commands.framework.paths import Paths
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.util import symlink


class CommandPath:
    """Read search paths for command scripts from the configuration."""

    def __init__(self, include_patterns, exclude_patterns):
        excluded_command_dirs = self._create_items(exclude_patterns)

        self.items = sorted([
            x for x in self._create_items(include_patterns)
            if x not in excluded_command_dirs
        ])

        basenames = [os.path.basename(x) for x in self.items]
        for basename in basenames:
            if basenames.count(basename) > 1:
                raise CommandError("More than 1 command path with name %s" %
                                   basename)

    def _create_items(self, patterns):
        result = []
        for pattern in patterns:
            for x in glob.glob(os.path.expanduser(pattern)):
                if os.path.isdir(
                        x) and not os.path.basename(x).startswith('_'):
                    result.append(x)
        return result

    def _create_search_path_dir(self):
        hash_code = hashlib.md5(json.dumps(
            self.items).encode('utf-8')).hexdigest()
        search_path_dir = os.path.join(Paths().global_config_dir(),
                                       "search_path", hash_code)

        if not os.path.exists(search_path_dir):
            os.makedirs(search_path_dir)
            open(os.path.join(search_path_dir, "__init__.py"), 'a').close()
            for item in self.items:
                basename = os.path.basename(item)
                target_path = os.path.join(search_path_dir, basename)
                if not os.path.exists(target_path):
                    symlink(item, target_path)

        return search_path_dir

    def extend_sys_path(self):
        search_path_dir = self._create_search_path_dir()
        if search_path_dir not in sys.path:
            sys.path.append(search_path_dir)


def get_command_path(config):
    root_config = config.get('ROOT', {})
    command_path = root_config.get('command_path', [])
    command_path_exclude = root_config.get('command_path_exclude', [])
    return CommandPath(include_patterns=command_path,
                       exclude_patterns=command_path_exclude)
