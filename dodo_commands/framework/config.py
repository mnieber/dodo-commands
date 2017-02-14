"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_expander import ConfigExpander
from dodo_commands.framework.config_expander import Key, KeyNotFound  # noqa
import glob
import os
import re
import sys
import yaml


def get_project_dir():
    """Return the root dir of the current project."""
    return os.environ['DODO_COMMANDS_PROJECT_DIR']


class ConfigIO:
    """Read and write the dodo configuration."""

    def __init__(self, config_base_dir=None):
        """Arg config_base_dir is where config files are searched.

        Arg config_base_dir defaults to get_project_dir()/dodo_commands/res.
        """
        self.config_base_dir = (
            os.path.join(get_project_dir(), "dodo_commands", "res")
            if config_base_dir is None
            else config_base_dir
        )

    def _path_to(self, post_fix_paths):
        """Return path composed of config_base_dir and post_fix_paths list."""
        return os.path.join(self.config_base_dir, *post_fix_paths)

    def _layers(self, config):
        result = []
        layer_dir = config.get('ROOT', {}).get('layer_dir', '')
        layers = config.get('ROOT', {}).get('layers', [])
        for layer_filename in layers:
            result.append(
                self._path_to([layer_dir, layer_filename])
            )
        return result

    def _add_layer(self, config, layer):
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

    def load(self, config_filename='config.yaml', load_layers=True):
        """Get configuration."""
        full_config_filename = self._path_to([config_filename])
        if not os.path.exists(full_config_filename):
            return None

        with open(full_config_filename) as f:
            config = yaml.load(f.read())
        if load_layers:
            for layer_filename in self._layers(config):
                if os.path.exists(layer_filename):
                    self._add_layer(config, self.load(layer_filename))
                else:
                    print("Warning: layer not found: %s" % layer_filename)

        return config

    def save(self, config, config_filename='config.yaml'):
        """Write config to config_filename."""
        content = yaml.dump(config, default_flow_style=False, indent=4)
        with open(self._path_to([config_filename]), 'w') as f:
            formatted_content = re.sub(
                r'^([0-9_A-Z]+\:)$',
                r'\n\1',
                content,
                flags=re.MULTILINE
            )
            return f.write(
                # swallow the leading newline
                formatted_content[1:]
                if formatted_content[0] == '\n' else
                formatted_content
            )


def load_dodo_config():
    """Load the project's dodo config and expand it."""
    def _add_to_config(config, section, key, value):
        if section in config:
            if key not in config[section]:
                config[section][key] = value

    config = ConfigIO().load() or dict(ROOT={})
    project_dir = get_project_dir()
    _add_to_config(
        config, "ROOT", "project_name", os.path.basename(project_dir))
    _add_to_config(
        config, "ROOT", "project_dir", project_dir)
    _add_to_config(
        config,
        "ROOT",
        "res_dir",
        os.path.join(project_dir, "dodo_commands", "res"))
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

    def __init__(self, project_dir, config_base_dir=None):
        """config_base_dir is the directory where config files are searched.

        The config_base_dir arg defaults to project_dir/dodo_commands/res.
        """
        if config_base_dir is None:
            config_base_dir = os.path.join(project_dir, "dodo_commands", "res")

        config = load_dodo_config()
        excluded_dirs = [
            x.full_path for x in self._collect_items(
                config.get('ROOT', {}).get('command_path_exclude', []),
            )
        ]
        self.items = [
            x for x in self._collect_items(
                config.get('ROOT', {}).get('command_path', [])
            )
            if x.full_path not in excluded_dirs
        ]

    def _collect_items(self, patterns):
        items = []
        for pattern in patterns:
            try:
                prefix, postfix = pattern
                prefix = os.path.expanduser(prefix)
            except:
                raise CommandError(
                    "Items in command_path should be of " +
                    "type [<sys-path>, <module-path>]."
                )

            for command_dir in [
                x for x in glob.glob(os.path.join(prefix, postfix))
                if os.path.isdir(x)
            ]:
                item = CommandPath.Item()
                item.sys_path = prefix
                item.module_path = os.path.relpath(command_dir, prefix)
                items.append(item)
        return items

    def extend_sys_path(self):  # noqa
        for item in self.items:
            if item.sys_path not in sys.path:
                sys.path.append(item.sys_path)
