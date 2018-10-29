"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_expander import ConfigExpander
from dodo_commands.framework.config_expander import Key, KeyNotFound  # noqa
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import symlink
from six.moves import configparser
import glob
import json
import os
import re
import ruamel.yaml
import sys
import hashlib


def load_global_config_parser():
    config_parser = configparser.ConfigParser()
    config_parser.read(Paths().global_config_filename())
    return config_parser


def write_global_config_parser(config_parser):
    """Save configuration."""
    with open(Paths().global_config_filename(), "w") as f:
        config_parser.write(f)


_global_config = """[settings]
projects_dir=~/projects
python_interpreter=python
diff_tool=diff

[recent]
"""


def create_global_config():
    """Create config file and default_commands dir."""
    base_dir = Paths().global_config_dir()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    config_filename = Paths().global_config_filename()
    if not os.path.exists(config_filename):
        with open(config_filename, 'w') as f:
            f.write(_global_config)

    default_commands_dir = Paths().default_commands_dir()
    if not os.path.exists(default_commands_dir):
        os.mkdir(default_commands_dir)
        symlink(
            os.path.join(Paths().extra_dir(), "dodo_standard_commands"),
            os.path.join(Paths().default_commands_dir(),
                         "dodo_standard_commands"))

    init_py = os.path.join(default_commands_dir, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, 'w') as f:
            pass


def merge_into_config(config, layer, xpath=None):
    def _is_list(x):
        return isinstance(x, type(list()))

    def _is_dict(x):
        return isinstance(x, type(dict()))

    def _raise(xpath):
        raise CommandError("Cannot merge configurations. Check key /%s" %
                           '/'.join(new_xpath))

    xpath = xpath or []
    for key, val in (layer or {}).items():
        new_xpath = xpath + [key]

        if key not in config:
            config[key] = val
        elif _is_dict(val):
            if not _is_dict(config[key]):
                _raise(new_xpath)
            merge_into_config(config[key], val, new_xpath)
        elif _is_list(val):
            if not _is_list(config[key]):
                _raise(new_xpath)
            config[key].extend(val)
        else:
            config[key] = val


class ConfigIO:
    """Read and write the dodo configuration."""

    def __init__(self, config_base_dir=None):
        """Arg config_base_dir is where config files are searched.

        Arg config_base_dir defaults to Paths().res_dir().
        """
        self.config_base_dir = (Paths().res_dir() if config_base_dir is None
                                else config_base_dir)  # noqa

    def _path_to(self, post_fix_paths):
        """Return path composed of config_base_dir and post_fix_paths list."""
        return os.path.join(self.config_base_dir, *post_fix_paths)

    def get_layers(self, config):
        """Returns list of layer filenames"""

        def add_prefix(filename):
            return (filename
                    if filename.startswith('/') else self._path_to([filename]))

        patterns = [
            add_prefix(os.path.expanduser(pattern))
            for pattern in config.get('ROOT', {}).get('layers', [])
        ]

        result = []
        for pattern in patterns:
            result.extend([x for x in glob.glob(pattern)])
        return result

    def _load_layers(self, config):
        def layer_exists(layer_filename):
            if not os.path.exists(layer_filename):
                print("Warning: layer not found: %s" % layer_filename)
                return False
            return True

        layer_filenames = [
            x for x in self.get_layers(config) if layer_exists(x)
        ]
        layers = [self.load(x, load_layers=False) for x in layer_filenames]
        for layer in layers:
            merge_into_config(config, layer)

    def load(self, config_filename='config.yaml', load_layers=True):
        """Get configuration."""
        full_config_filename = self._path_to([config_filename])
        if not os.path.exists(full_config_filename):
            return None

        with open(full_config_filename) as f:
            config = ruamel.yaml.round_trip_load(f.read())
        if load_layers:
            self._load_layers(config)
        return config

    def save(self, config, config_filename='config.yaml'):
        """Write config to config_filename."""
        with open(self._path_to([config_filename]), 'w') as f:
            return f.write(ruamel.yaml.round_trip_dump(config))


class ConfigLoader:
    """Load the project's dodo config and expand it."""

    def _add_to_config(self, config, section, key, value):
        if section in config:
            if key not in config[section]:
                config[section][key] = value

    def _system_commands_dir(self):
        """Return directory where system command scripts are stored"""
        import dodo_commands.dodo_system_commands
        return os.path.dirname(dodo_commands.dodo_system_commands.__file__)

    def _extend_config(self, config):
        """Add special values to the project's config"""
        project_dir = Paths().project_dir()
        if project_dir:
            self._add_to_config(config, "ROOT", "project_name",
                                os.path.basename(project_dir))
            self._add_to_config(config, "ROOT", "project_dir", project_dir)
            self._add_to_config(config, "ROOT", "res_dir", Paths().res_dir())

    def _extend_command_path(self, config):
        """Add the system commands to the command path"""
        self._add_to_config(config, "ROOT", "command_path", [])
        config['ROOT']['command_path'].append(self._system_commands_dir())

    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    def load(self, config_base_dir=None):
        fallback_config = dict(ROOT={})
        try:
            config = ConfigIO(config_base_dir).load() or fallback_config
        except ruamel.yaml.scanner.ScannerError:
            config = fallback_config
            self._report(
                "There was an error while loading the configuration. "
                "Run 'dodo diff' to compare your configuration to the "
                "default one.\n")

        self._extend_command_path(config)
        self._extend_config(config)
        ConfigExpander().run(config)
        return config


class CommandPath:
    """Read search paths for command scripts from the configuration."""

    def __init__(self, config):
        exclude_patterns = self._exclude_patterns(config)
        excluded_command_dirs = self._create_items(exclude_patterns)

        include_patterns = self._include_patterns(config)
        self.items = sorted([
            x for x in self._create_items(include_patterns)
            if x not in excluded_command_dirs
        ])

        basenames = [os.path.basename(x) for x in self.items]
        for basename in basenames:
            if basenames.count(basename) > 1:
                raise CommandError("More than 1 command path with name %s" %
                                   basename)

    def _include_patterns(self, config):
        return config.get('ROOT', {}).get('command_path', [])

    def _exclude_patterns(self, config):
        return config.get('ROOT', {}).get('command_path_exclude', [])

    def _create_items(self, patterns):
        result = []
        for pattern in patterns:
            for x in glob.glob(os.path.expanduser(pattern)):
                if os.path.isdir(x):
                    result.append(x)
        return result

    def _create_search_path_dir(self):
        hash_code = hashlib.md5(json.dumps(self.items).encode(
            'utf-8')).hexdigest()
        search_path_dir = os.path.join(Paths().global_config_dir(),
                                       "search_path", hash_code)

        if not os.path.exists(search_path_dir):
            os.makedirs(search_path_dir)
            open(os.path.join(search_path_dir, "__init__.py"), 'a').close()
            for item in self.items:
                basename = os.path.basename(item)
                symlink(item, os.path.join(search_path_dir, basename))

        return search_path_dir

    def extend_sys_path(self):  # noqa
        search_path_dir = self._create_search_path_dir()
        if search_path_dir not in sys.path:
            sys.path.append(search_path_dir)


def look_up_key(config, key, default_value="__not_set_234234__"):
    xpath = [k for k in key.split("/") if k]
    try:
        return Key(config, xpath).get()
    except KeyNotFound:
        if default_value == "__not_set_234234__":
            raise
    return default_value


def expand_keys(config, text):
    result = ""
    val_terms = re.split('\$\{([^\}]+)\}', text)
    for idx, term in enumerate(val_terms):
        if idx % 2:
            str_rep = json.dumps(look_up_key(config, term))
            if str_rep.startswith('"') and str_rep.endswith('"'):
                str_rep = str_rep[1:-1]
            result += str_rep
        else:
            result += term
    return result
