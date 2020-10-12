from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.util import xpath_to_string


class KeyNotFound(CommandError):
    """Raised if an xpath is not found in a configuration."""

    pass


class Key:
    """Access a nested value in a dict."""

    def __init__(self, config, xpath_or_str):  # noqa
        self.config = config

        def split_on_slash(key):
            return [k for k in key[1:].split("/") if k]

        # the list of sub-keys along the path to an item in self.config
        self.xpath = (
            split_on_slash(xpath_or_str)
            if isinstance(xpath_or_str, str)
            else xpath_or_str
        )

    def _step_into(self, node, subkey):
        try:
            if isinstance(node, type(dict())):
                return node[subkey]
            if isinstance(node, type(list())):
                return node[int(subkey)]
        except:  # noqa
            raise KeyNotFound("Cannot get value at %s\n" % self)

    def exists(self):
        config_node = self.config
        for xpath_node in self.xpath:
            if isinstance(config_node, dict) and xpath_node in config_node:
                config_node = config_node[xpath_node]
            elif isinstance(config_node, list) and int(xpath_node) < len(config_node):
                config_node = config_node[int(xpath_node)]
            else:
                return False
        return True

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
        return xpath_to_string(self.xpath)
