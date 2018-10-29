from dodo_commands.framework.command_error import CommandError
import os
import re
import sys


class KeyNotFound(CommandError):
    """Raised if an xpath is not found in a configuration."""
    pass


class DictKey:
    def __init__(self, the_dict, the_key, xpath):
        self.dict = the_dict
        self.key = the_key
        self.xpath = xpath

    def __repr__(self):  # noqa
        return "DK[%s]" % self.key

    def warning_msg_not_expanded(self):
        return "Unexpanded key {key} at location /{xpath}".format(
            key=self.key, xpath='/'.join([str(x) for x in self.xpath]))

    def create_dict_val(self, expanded_key):  # noqa
        if expanded_key != self.key:
            self.dict[expanded_key] = self.dict[self.key]
            del self.dict[self.key]
        return DictVal(self.dict, expanded_key, self.xpath)


class DictVal:
    def __init__(self, the_dict, the_key, xpath):
        self.dict = the_dict
        self.key = the_key
        self.xpath = xpath

    def get_value(self):
        return self.dict[self.key]

    def replace_value(self, new_value):
        self.dict[self.key] = new_value

    def must_eval(self):
        return (isinstance(self.xpath[-1], str) and
                self.xpath[-1].endswith('_EVAL') or
                (len(self.xpath) >= 2 and isinstance(self.xpath[-2], str) and
                 self.xpath[-2].endswith('_EVAL')))

    def warning_msg_not_expanded(self):
        return "Unexpanded value {val} at location /{xpath}".format(
            val=self.get_value(), xpath='/'.join([str(x) for x in self.xpath]))

    def __repr__(self):  # noqa
        return "DV[%s]" % self.key


class ListVal:
    def __init__(self, the_list, the_idx, xpath):
        self.idx = the_idx
        self.list = the_list
        self.xpath = xpath

    def get_value(self):
        return self.list[self.idx]

    def replace_value(self, new_value):
        self.list[self.idx] = new_value

    def must_eval(self):
        return (len(self.xpath) >= 2 and isinstance(self.xpath[-2], str) and
                self.xpath[-2].endswith('_EVAL'))

    def warning_msg_not_expanded(self):
        return "Unexpanded value {val} at location /{xpath}".format(
            val=self.get_value(), xpath='/'.join([str(x) for x in self.xpath]))

    def __repr__(self):  # noqa
        return "L[%s]" % self.idx


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

    def exists(self):
        config_node = self.config
        for xpath_node in self.xpath:
            if isinstance(config_node, dict) and xpath_node in config_node:
                config_node = config_node[xpath_node]
            elif isinstance(config_node,
                            list) and int(xpath_node) < len(config_node):
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
        return "/" + "/".join([str(x) for x in self.xpath])


class ConfigExpander:
    """Expand environment variables and references in the config."""

    _key_regexp = r"\$\{(/[^\}]*)\}"

    @classmethod
    def _get_xpath_from_string(cls, xpath_string):
        return tuple([ix for ix in xpath_string.split("/") if ix])

    def _expand_str(self, current_str):
        expanded_str = current_str
        key_expressions = [
            x for x in re.finditer(self._key_regexp, current_str)
        ]
        known_strs = []

        while (key_expressions):
            changed = False
            for key_expression in reversed(key_expressions):
                xpath_string = key_expression.group(1)
                xpath = self._get_xpath_from_string(xpath_string)

                key = Key(self.config, xpath)
                if key.exists():
                    expanded_str = (
                        expanded_str[:key_expression.start()] + str(key.get())
                        + expanded_str[key_expression.end():])

                    if expanded_str not in known_strs:
                        known_strs.append(expanded_str)
                        changed = True

            if not changed:
                return None

            current_str = expanded_str
            key_expressions = [
                x for x in re.finditer(self._key_regexp, current_str)
            ]

        return os.path.expandvars(expanded_str)

    def _expand(self, raw_obj):
        if isinstance(raw_obj, str):
            return self._expand_str(raw_obj)

        if isinstance(raw_obj, list):
            return [self._expand(x) for x in raw_obj]

        if isinstance(raw_obj, dict):
            return {
                self._expand(k): self._expand(v)
                for k, v in raw_obj.items()
            }

        return raw_obj

    def _schedule_children(self, obj, todo, xpath):
        if isinstance(obj, dict):
            for k in obj:
                todo.append(DictKey(obj, k, xpath + [k]))
            return True
        if isinstance(obj, list):
            for idx in range(len(obj)):
                todo.append(ListVal(obj, idx, xpath + [idx]))
            return True

    def _eval(self, value, xpath):
        try:
            return eval(value)
        except:
            raise CommandError(
                "Cannot evaluate {value} at location {xpath}".format(
                    value=value, xpath=xpath))

    def run(self, config):  # noqa
        nodes = []
        self.config = config
        self._schedule_children(config, nodes, [])

        changed = True
        while len(nodes) and changed:
            changed = False
            new_nodes = list()
            for node in nodes:
                if isinstance(node, DictKey):
                    expanded_key = self._expand(node.key)
                    if expanded_key is None:
                        new_nodes.append(node)
                    else:
                        changed = True
                        new_nodes.append(node.create_dict_val(expanded_key))
                elif isinstance(node, DictVal) or isinstance(node, ListVal):
                    value = node.get_value()
                    if self._schedule_children(value, new_nodes, node.xpath):
                        changed = True
                    else:
                        expanded_value = self._expand(value)
                        if expanded_value is None:
                            new_nodes.append(node)
                        else:
                            changed = True
                            node.replace_value(
                                self._eval(expanded_value, node.xpath)
                                if node.must_eval() else expanded_value)
                else:
                    raise CommandError("Should not reach here")
            nodes = new_nodes

        for node in nodes:
            sys.stderr.write("Warning: %s\n" % node.warning_msg_not_expanded())
