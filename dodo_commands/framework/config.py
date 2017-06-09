"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_expander import ConfigExpander
from dodo_commands.framework.config_expander import Key, KeyNotFound  # noqa
import glob
import os
import sys
import ruamel.yaml


def get_project_dir():
    """Return the root dir of the current project."""
    return os.environ['DODO_COMMANDS_PROJECT_DIR']


def _default_config_base_dir(project_dir):
    return os.path.join(project_dir, "dodo_commands", "res")


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
        result = []
        root = config.get('ROOT', {})
        layer_dir = root.get('layer_dir', '')
        for layer_filename in root.get('layers', []):
            pattern = os.path.expanduser(
                layer_filename
                if os.path.dirname(layer_filename) else
                self._path_to([layer_dir, layer_filename])
            )
            result.extend(x for x in glob.glob(pattern))
        return result

    def _add_layer_to_config(self, config, layer):
        for section in (layer or {}):
            if section not in config:
                config[section] = layer[section]
                continue
            for key, value in layer[section].items():
                has_key = key in config[section]
                if has_key and isinstance(value, type(dict())):
                    config[section][key].update(value)
                elif has_key and isinstance(value, type(list())):
                    config[section][key].extend(value)
                else:
                    config[section][key] = value

    def _load_layers(self, config):
        for layer_filename in self._layers(config):
            if os.path.exists(layer_filename):
                self._add_layer_to_config(
                    config, self.load(layer_filename, load_layers=False)
                )
            else:
                print("Warning: layer not found: %s" % layer_filename)

    def load(self, config_filename='config.yaml', load_layers=True):
        """Get configuration."""
        if not get_project_dir():
            return None

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

    def load(self, config_base_dir=None):
        config = ConfigIO(config_base_dir).load() or dict(ROOT={})
        self._extend_command_path(config)
        self._extend_config(config)
        ConfigExpander().run(config)
        return config


def load_dodo_config(config_base_dir=None):
    return ConfigLoader().load(config_base_dir)


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
