import glob
import os

from dodo_commands.dependencies.get import yaml
from dodo_commands.framework.paths import Paths


class ConfigIO:
    """Read and writes dodo configuration (yaml) files."""
    def __init__(self, config_base_dir=None):
        """Arg config_base_dir is where config files are searched.

        Arg config_base_dir defaults to Paths().res_dir().
        """
        self._cache = {}
        self.config_base_dir = (Paths().res_dir() if config_base_dir is None
                                else config_base_dir)

    def _path_to(self, post_fix_paths):
        """Return path composed of config_base_dir and post_fix_paths list."""
        return os.path.join(self.config_base_dir, *post_fix_paths)

    def glob(self, patterns):
        """Returns list of filenames"""
        def add_prefix(filename):
            return (filename
                    if filename.startswith('/') else self._path_to([filename]))

        patterns = [
            add_prefix(os.path.expanduser(pattern)) for pattern in patterns
        ]

        result = []
        for pattern in patterns:
            result.extend([x for x in glob.glob(pattern)])
        return result

    def load(self, config_filename='config.yaml'):
        """Get configuration."""
        full_config_filename = self._path_to([config_filename])

        if full_config_filename in self._cache:
            return self._cache[full_config_filename]

        if not os.path.exists(full_config_filename):
            return None

        with open(full_config_filename) as f:
            config = yaml.round_trip_load(f.read())

        self._cache[full_config_filename] = config
        return config

    def save(self, config, config_filename='config.yaml'):
        """Write config to config_filename."""
        with open(self._path_to([config_filename]), 'w') as f:
            return f.write(yaml.round_trip_dump(config))
