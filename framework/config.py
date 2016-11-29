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

    def remove(self):  # noqa
        node = self.config
        for key in self.subkeys[:-1]:
            node = self._step_into(node, key)
        del node[self.subkeys[-1]]

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
    def _expand(cls, value, config, processed_keys):
        matches = re.finditer(cls._regexp, value)
        for match in reversed([m for m in matches]):
            replacement = cls._key_for_match(match.group(1), config)
            if replacement.subkeys not in processed_keys:
                return False, None
            value = (
                value[:match.start()] +
                str(replacement.get()) +
                value[match.end():]
            )
        return True, os.path.expandvars(value)

    @classmethod
    def _expand_value_for(cls, key, processed_keys):
        value = key.get()
        if not cls._is_leaf(value):
            return cls._is_fully_expanded(key, processed_keys), None
        if not isinstance(value, type(str())):
            return True, None
        return cls._expand(
            value, key.config, processed_keys
        )

    @classmethod
    def _for_each_key(cls, config, node, f, subkeys=None):
        if subkeys is None:
            subkeys = []

        for child_key in cls._subkeys_of(node):
            value = node[child_key]
            f(config, list(subkeys) + [child_key])
            cls._for_each_key(
                config, value, f, list(subkeys) + [child_key]
            )

    @classmethod
    def _expanded_key(cls, key, processed_keys):
        """Return key with variable expansion on last subkey.

        Return None if not all variables could be expanded.
        """
        last_index = key.subkeys[-1]
        if not isinstance(last_index, type(str())):
            return key

        is_expanded, expanded_last_index = cls._expand(
            last_index, key.config, processed_keys
        )
        if not is_expanded:
            return None
        return Key(
            key.config, key.subkeys[:-1] + [expanded_last_index]
        )

    @classmethod
    def run(cls, config):  # noqa
        all_keys = []
        cls._for_each_key(
            config, config,
            lambda config, subkeys: all_keys.append(Key(config, subkeys))
        )

        processed_keys = []
        while all_keys:
            for key in list(all_keys):
                expanded_key = cls._expanded_key(key, processed_keys)
                if expanded_key is None:
                    continue

                is_expanded, expanded_value = cls._expand_value_for(
                    key, processed_keys
                )

                if is_expanded:
                    if expanded_value is not None:
                        expanded_key.set(expanded_value)
                        if expanded_key.subkeys != key.subkeys:
                            key.remove()
                    if cls._must_evaluate(expanded_key):
                        cls._evaluate(expanded_key)
                    processed_keys.append(expanded_key.subkeys)
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
