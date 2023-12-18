import os
import re

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_key import Key
from dodo_commands.framework.util import EnvironMemo, xpath_to_string


class DictKey:
    def __init__(self, the_dict, the_key, xpath):
        self.dict = the_dict
        self.key = the_key
        self.xpath = xpath

    def __repr__(self):  # noqa
        return "DK[%s]" % self.key

    def warning_msg_not_expanded(self):
        return "Unexpanded key {key} at location {xpath}".format(
            key=self.key, xpath=xpath_to_string(self.xpath)
        )

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

    def warning_msg_not_expanded(self):
        return "Unexpanded value {val} at location {xpath}".format(
            val=self.get_value(), xpath=xpath_to_string(self.xpath)
        )

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

    def warning_msg_not_expanded(self):
        return "Unexpanded value {val} at location {xpath}".format(
            val=self.get_value(), xpath=xpath_to_string(self.xpath)
        )

    def __repr__(self):  # noqa
        return "L[%s]" % self.idx


def get_key_expressions(search_string, key_regexp):
    return [x for x in re.finditer(key_regexp, search_string)]


class ConfigExpander:
    """Expand environment variables and references in the config."""

    KEY_REGEXP = re.compile(r"\$\{(/[^\}]*)\}")
    ENV_KEY_REGEXP = re.compile(r"\$\{([^\}]*)\}")

    def __init__(self, extra_vars=None):
        self.extra_vars = extra_vars or {}

    def _expand_str(self, current_str):
        expanded_str = current_str
        key_expressions = get_key_expressions(current_str, ConfigExpander.KEY_REGEXP)
        known_strs = []

        while key_expressions:
            changed = False
            for key_expression in reversed(key_expressions):
                xpath_string = key_expression.group(1)

                key = Key(self.config, xpath_string)
                if key.exists():
                    expanded_str = "".join(
                        [
                            expanded_str[: key_expression.start()],
                            str(key.get()),
                            expanded_str[key_expression.end() :],
                        ]
                    )

                    if expanded_str not in known_strs:
                        known_strs.append(expanded_str)
                        changed = True

            if not changed:
                return None

            current_str = expanded_str
            key_expressions = get_key_expressions(
                current_str, ConfigExpander.KEY_REGEXP
            )

        with EnvironMemo(self.extra_vars):
            expanded_str = os.path.expandvars(expanded_str)

        env_key_expressions = get_key_expressions(
            expanded_str, ConfigExpander.ENV_KEY_REGEXP
        )
        return expanded_str if not env_key_expressions else None

    def _expand(self, raw_obj):
        if isinstance(raw_obj, str):
            return self._expand_str(raw_obj)

        if isinstance(raw_obj, list):
            return [self._expand(x) for x in raw_obj]

        if isinstance(raw_obj, dict):
            return {self._expand(k): self._expand(v) for k, v in raw_obj.items()}

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

    def run(self, config, callbacks=None):  # noqa
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

                            node.replace_value(expanded_value)
                            if xpath_to_string(node.xpath) in (callbacks or {}):
                                callbacks[xpath_to_string(node.xpath)](expanded_value)
                else:
                    raise CommandError("Should not reach here")

            nodes = new_nodes

        warnings = ["Warning: %s\n" % node.warning_msg_not_expanded() for node in nodes]
        return warnings
