"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
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


class KeyNotFound(CommandError):
    """Raised if an xpath is not found in a configuration."""

    pass


class Key:
    """Access a nested value in a dict."""

    def __init__(self, config, xpath):  # noqa
        self.config = config
        # the list of sub-keys along the path to an item in self.config
        self.xpath = xpath

    def child(self, subkey):
        """Return key for child with subkey."""
        return Key(self.config, list(self.xpath) + [subkey])

    def _step_into(self, node, subkey):
        try:
            if isinstance(node, type(dict())):
                return node[subkey]
            if isinstance(node, type(list())):
                return node[int(subkey)]
        except:
            raise KeyNotFound("Cannot get value at %s\n" % self)

    def get(self):  # noqa
        node = self.config
        for subkey in self.xpath:
            node = self._step_into(node, subkey)
        return node

    def set(self, value):  # noqa
        node = self.config
        for subkey in self.xpath[:-1]:
            node = self._step_into(node, subkey)
        node[self.xpath[-1]] = value

    def remove(self):  # noqa
        node = self.config
        for subkey in self.xpath[:-1]:
            node = self._step_into(node, subkey)
        del node[self.xpath[-1]]

    def __repr__(self):  # noqa
        return str(self.xpath)


class ConfigExpander:
    """Expand environment variables and references in the config."""

    _regexp = r"\$\{(/[^\}]*)\}"

    @classmethod
    def _is_fully_expanded(cls, key, processed_xpaths):
        if key.xpath in processed_xpaths:
            return True

        value = key.get()
        if cls._is_leaf(value):
            return False

        return all([
            cls._is_fully_expanded(key.child(x), processed_xpaths)
            for x in cls._subkeys_of(value)
        ])

    @classmethod
    def _must_evaluate(cls, key):
        last_subkey = key.xpath[-1]
        return (
            isinstance(last_subkey, type(str())) and
            last_subkey.endswith("_EVAL")
        )

    @classmethod
    def _evaluate(cls, key):
        value = key.get()
        if cls._is_leaf(value):
            try:
                key.set(eval(value))
            except:
                raise CommandError(
                    "Cannot evaluate value '%s' for key %s\n" % (value, key)
                )
        else:
            for k in cls._subkeys_of(value):
                if cls._is_leaf(value[k]):
                    cls._evaluate(key.child(k))

    @classmethod
    def _is_leaf(cls, value):
        return not(
            isinstance(value, type(dict())) or
            isinstance(value, type(list()))
        )

    @classmethod
    def _subkeys_of(cls, value):
        if isinstance(value, type(dict())):
            return [k for k in value]
        if isinstance(value, type(list())):
            return range(len(value))
        return []

    @classmethod
    def _key_for_match(cls, matched_str, config):
        key = Key(config, [])
        for index in [ix for ix in matched_str.split("/") if ix]:
            if isinstance(key.get(), type(list())):
                subkey = int(index)
            else:
                subkey = index
            key = key.child(subkey)
        return key

    @classmethod
    def _expand(cls, value, config, processed_xpaths):
        matches = re.finditer(cls._regexp, value)
        for match in reversed([m for m in matches]):
            replacement = cls._key_for_match(match.group(1), config)
            if replacement.xpath not in processed_xpaths:
                return False, None
            value = (
                value[:match.start()] +
                str(replacement.get()) +
                value[match.end():]
            )
        return True, os.path.expandvars(value)

    @classmethod
    def _expand_value_for(cls, key, processed_xpaths):
        value = key.get()
        if not cls._is_leaf(value):
            return cls._is_fully_expanded(key, processed_xpaths), None
        if not isinstance(value, type(str())):
            return True, None
        return cls._expand(
            value, key.config, processed_xpaths
        )

    @classmethod
    def _for_each_xpath(cls, config, node, f, xpath=None):
        if xpath is None:
            xpath = []

        for subkey in cls._subkeys_of(node):
            value = node[subkey]
            f(config, list(xpath) + [subkey])
            cls._for_each_xpath(
                config, value, f, list(xpath) + [subkey]
            )

    @classmethod
    def _expanded_key(cls, key, processed_xpaths):
        """Return key with variable expansion on last subkey.

        Return None if not all variables could be expanded.
        """
        last_subkey = key.xpath[-1]
        if not isinstance(last_subkey, type(str())):
            return key

        is_expanded, expanded_last_subkey = cls._expand(
            last_subkey, key.config, processed_xpaths
        )
        if not is_expanded:
            return None
        return Key(
            key.config, key.xpath[:-1] + [expanded_last_subkey]
        )

    @classmethod
    def run(cls, config):  # noqa
        all_keys = []
        cls._for_each_xpath(
            config, config,
            lambda config, xpath: all_keys.append(Key(config, xpath))
        )

        processed_xpaths = []
        while all_keys:
            for key in list(all_keys):
                expanded_key = cls._expanded_key(key, processed_xpaths)
                if expanded_key is None:
                    continue

                is_expanded, expanded_value = cls._expand_value_for(
                    key, processed_xpaths
                )

                if is_expanded:
                    if expanded_value is not None:
                        expanded_key.set(expanded_value)
                        if expanded_key.xpath != key.xpath:
                            key.remove()
                    if cls._must_evaluate(expanded_key):
                        cls._evaluate(expanded_key)
                    processed_xpaths.append(expanded_key.xpath)
                    all_keys.remove(key)


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
