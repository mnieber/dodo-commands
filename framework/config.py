"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
import glob
import yaml
import os
import re
import sys


def get_project_dir():
    """Return the root folder of the current project."""
    result = __file__
    for _ in range(3):
        result = os.path.dirname(result)
    return result


class ConfigIO:
    """Read and write the dodo configuration."""

    @classmethod
    def _path_to(cls, post_fix_paths):
        """Return path composed of dodo folder and the post_fix_paths list."""
        return os.path.join(
            get_project_dir(),
            "dodo_commands",
            *post_fix_paths
        )

    @classmethod
    def _layers(cls, config):
        result = []
        layer_dir = config.get('ROOT', {}).get('layer_dir', '')
        layers = config.get('ROOT', {}).get('layers', [])
        for layer_filename in layers:
            result.append(
                ConfigIO._path_to([layer_dir, layer_filename])
            )
        return result

    @classmethod
    def _add_layer(cls, config, layer):
        for section in (layer or {}):
            if section not in config:
                config[section] = layer[section]
                continue
            for key, value in layer[section].iteritems():
                has_key = key in config[section]
                if has_key and isinstance(value, type(dict())):
                    config[section][key].update(value)
                elif has_key and isinstance(value, type(list())):
                    config[section][key].extend(value)
                else:
                    config[section][key] = value

    @classmethod
    def load(cls, config_filename='config.yaml', load_layers=True):
        """Get configuration."""
        full_config_filename = cls._path_to([config_filename])
        if not os.path.exists(full_config_filename):
            return None

        with open(full_config_filename) as f:
            config = yaml.load(f.read())
        if load_layers:
            for layer_filename in cls._layers(config):
                if os.path.exists(layer_filename):
                    cls._add_layer(config, cls.load(layer_filename))
                else:
                    print("Warning: layer not found: %s" % layer_filename)
        return config

    @classmethod
    def save(cls, config, config_filename='config.yaml'):
        """Write config to config_filename."""
        content = yaml.dump(config, default_flow_style=False, indent=4)
        with open(cls._path_to([config_filename]), 'w') as f:
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


class KeyNotFound(CommandError):
    """Raised if a key is not found in a configuration."""

    pass


class Key:
    """Access a nested value in a dict."""

    def __init__(self, config, subkeys):  # noqa
        self.config = config
        self.subkeys = subkeys

    def child(self, subkey):
        """Return key for child with subkey."""
        return Key(self.config, list(self.subkeys) + [subkey])

    def _step_into(self, node, key):
        try:
            if isinstance(node, type(dict())):
                return node[key]
            if isinstance(node, type(list())):
                return node[int(key)]
        except:
            raise KeyNotFound("Cannot get value at %s\n" % self)

    def get(self):  # noqa
        node = self.config
        for key in self.subkeys:
            node = self._step_into(node, key)
        return node

    def set(self, value):  # noqa
        node = self.config
        for key in self.subkeys[:-1]:
            node = self._step_into(node, key)
        node[self.subkeys[-1]] = value

    def __repr__(self):  # noqa
        return str(self.subkeys)


class ConfigExpander:
    """Expand environment variables and references in the config."""

    _regexp = r"\$\{(/[^\}]*)\}"

    @classmethod
    def _is_fully_expanded(cls, key, processed_keys):
        if key.subkeys in processed_keys:
            return True

        value = key.get()
        if cls._is_leaf(value):
            return False

        return all([
            cls._is_fully_expanded(key.child(x), processed_keys)
            for x in cls._subkeys_of(value)
        ])

    @classmethod
    def _must_evaluate(cls, key):
        last_subkey = key.subkeys[-1]
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
    def _expand(cls, key, processed_keys):
        value = key.get()
        if not cls._is_leaf(value):
            return cls._is_fully_expanded(key, processed_keys)
        if not isinstance(value, type(str())):
            return True

        matches = re.finditer(cls._regexp, value)
        for match in reversed([m for m in matches]):
            replacement = Key(key.config, [])
            for index in [ix for ix in match.group(1).split("/") if ix]:
                if isinstance(replacement.get(), type(list())):
                    subkey = int(index)
                else:
                    subkey = index
                replacement = replacement.child(subkey)

            if replacement.subkeys not in processed_keys:
                return False
            value = (
                value[:match.start()] +
                str(replacement.get()) +
                value[match.end():]
            )

        key.set(os.path.expandvars(value))
        return True

    @classmethod
    def _collect_keys(cls, config, node, result, subkeys=None):
        if subkeys is None:
            subkeys = []

        for child_key in cls._subkeys_of(node):
            value = node[child_key]
            result.append(Key(config, list(subkeys) + [child_key]))
            cls._collect_keys(
                config, value, result, list(subkeys) + [child_key]
            )

    @classmethod
    def run(cls, config):  # noqa
        all_keys = []
        processed_keys = []
        cls._collect_keys(config, config, all_keys)
        while all_keys:
            for key in list(all_keys):
                if cls._expand(key, processed_keys):
                    if cls._must_evaluate(key):
                        cls._evaluate(key)
                    processed_keys.append(key.subkeys)
                    all_keys.remove(key)


class CommandPaths:
    """Read search paths for command scripts from the configuration."""

    class Item:  # noqa
        sys_path = ""
        module_path = ""

        @property
        def full_path(self):  # noqa
            return os.path.join(self.sys_path, self.module_path)

    def __init__(self, project_dir):  # noqa
        config = ConfigIO().load(load_layers=False) or {}
        self.items = []

        for pattern in config.get('ROOT', {}).get('command_paths', []):
            prefix = project_dir
            postfix = pattern
            if isinstance(pattern, type(list())):
                prefix = os.path.join(project_dir, pattern[0])
                postfix = pattern[1]

            for folder in [
                x for x in glob.glob(os.path.join(prefix, postfix))
                if os.path.isdir(x)
            ]:
                item = CommandPaths.Item()
                item.sys_path = prefix
                item.module_path = os.path.relpath(folder, prefix)
                self.items.append(item)

    def extend_sys_path(self):
        """Return relative paths (to sys.path) to the command scipt modules."""
        for item in self.items:
            if item.sys_path not in sys.path:
                sys.path.append(item.sys_path)
