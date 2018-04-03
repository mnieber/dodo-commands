"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_expander import ConfigExpander
from dodo_commands.framework.config_expander import Key, KeyNotFound  # noqa
from six.moves import configparser
import glob
import json
import os
import re
import ruamel.yaml
import sys


def get_global_config():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.dodo_commands/config"))
    return config


def get_project_dir():
    """Return the root dir of the current project."""
    return os.environ['DODO_COMMANDS_PROJECT_DIR']


def _default_config_base_dir(project_dir):
    return os.path.join(project_dir, "dodo_commands", "res")


def merge_into_config(config, layer, xpath=None):
    def _is_list(x):
        return isinstance(x, type(list()))

    def _is_dict(x):
        return isinstance(x, type(dict()))

    def _raise(xpath):
        raise CommandError(
            "Cannot merge configurations. Check key /%s" % '/'.join(new_xpath)
        )

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

        Arg config_base_dir defaults to get_project_dir()/dodo_commands/res.
        """
        self.config_base_dir = (
            _default_config_base_dir(get_project_dir())
            if config_base_dir is None else
            config_base_dir
        )

    def _path_to(self, post_fix_paths):
        """Return path composed of config_base_dir and post_fix_paths list."""
        return os.path.join(self.config_base_dir, *post_fix_paths)

    def _layers(self, config):
        """Returns list of layer filenames"""
        def add_prefix(filename):
            return (
                filename
                if filename.startswith('/') else
                self._path_to([filename])
            )

        patterns = [
            add_prefix(os.path.expanduser(pattern))
            for pattern in
            config.get('ROOT', {}).get('layers', [])
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

        layer_filenames = [x for x in self._layers(config) if layer_exists(x)]
        layers = [
            self.load(x, load_layers=False)
            for x in layer_filenames
        ]
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
        import dodo_commands.system_commands
        return os.path.dirname(dodo_commands.system_commands.__file__)

    def _extend_config(self, config):
        """Add special values to the project's config"""
        project_dir = get_project_dir()
        if project_dir:
            self._add_to_config(
                config, "ROOT", "project_name", os.path.basename(project_dir))
            self._add_to_config(
                config, "ROOT", "project_dir", project_dir)
            self._add_to_config(
                config,
                "ROOT",
                "res_dir",
                _default_config_base_dir(project_dir)
            )

    def _extend_command_path(self, config):
        """Add the system commands to the command path"""
        self._add_to_config(config, "ROOT", "command_path", [])
        config['ROOT']['command_path'].append(
            [os.path.dirname(self._system_commands_dir()), "system_commands"]
        )

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
                "default one.\n"
            )

        self._extend_command_path(config)
        self._extend_config(config)
        ConfigExpander().run(config)
        return config


class CommandPath:
    """Read search paths for command scripts from the configuration."""

    class Item:  # noqa
        sys_path = ""
        module_path = ""

        @property
        def full_path(self):  # noqa
            return os.path.join(self.sys_path, self.module_path)

    def __init__(self, config):
        """config_base_dir is the directory where config files are searched.

        The config_base_dir arg defaults to_
        _default_project_base_dir(project_dir).
        """
        exclude_patterns = self._exclude_patterns(config)
        excluded_command_dirs = [
            x.full_path for x in self._create_items(exclude_patterns)
        ]

        include_patterns = self._include_patterns(config)
        self.items = [
            x for x in self._create_items(include_patterns)
            if x.full_path not in excluded_command_dirs
        ]

    def _include_patterns(self, config):
        return config.get('ROOT', {}).get('command_path', [])

    def _exclude_patterns(self, config):
        return config.get('ROOT', {}).get('command_path_exclude', [])

    def _create_items(self, patterns):
        items = []
        for pattern in patterns:
            sys_path, module_path = self._split_pattern(pattern)
            for command_dir in self._glob_command_dirs(sys_path, module_path):
                items.append(self._create_item(sys_path, command_dir))
        return items

    def _create_item(self, sys_path, command_dir):
        item = CommandPath.Item()
        item.sys_path = sys_path
        item.module_path = os.path.relpath(command_dir, sys_path)
        return item

    def _glob_command_dirs(self, sys_path, module_path):
        return [
            x for x in glob.glob(os.path.join(sys_path, module_path))
            if os.path.isdir(x)
        ]

    def _split_pattern(self, pattern):
        try:
            sys_path, module_path = pattern
            sys_path = os.path.expanduser(sys_path)
        except:
            raise CommandError(
                "Patterns in command_path should be of " +
                "type [<sys-path>, <module-path>]. " +
                "Failing pattern: %s" % pattern
            )
        return sys_path, module_path

    def extend_sys_path(self):  # noqa
        for item in self.items:
            if item.sys_path not in sys.path:
                sys.path.append(item.sys_path)


def look_up_key(config, key, default_value="__not_set_234234__"):
    xpath = [k for k in key.split("/") if k]
    try:
        return Key(config, xpath).get()
    except KeyNotFound:
        if default_value == "__not_set_234234__":
            raise
    return default_value


def expand_keys(text, config):
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
