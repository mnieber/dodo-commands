from dodo_commands.framework.command_error import CommandError
import os
import re


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
        changed = True
        while all_keys and changed:
            changed = False
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
                    changed = True

        if all_keys:
            print("Warning: unexpanded keys %s" % all_keys)
