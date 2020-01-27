from funcy.py2 import distinct, merge

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.funcy import drill, for_each


def get_inferred_command_map(
    global_aliases,
    target_path_by_alias,
    layer_by_alias_target_path,
):
    layer_alias_by_inferred_command = {}

    for alias, target_path in target_path_by_alias.items():

        def get_layer(target_path):
            return layer_by_alias_target_path[target_path]

        def get_inferred_commands(layer):
            return drill(layer, 'ROOT', 'inferred_commands', default=[])

        def get_cmd_aliases(layer):
            command_aliases = drill(layer, 'ROOT', 'aliases', default={})
            for alias, target in global_aliases.items():
                if alias in command_aliases:
                    raise CommandError(
                        "Ambigous command alias %s, could be %s or %s" %
                        (alias, target, command_aliases[alias]))
            return merge(command_aliases, global_aliases)

        def get_inferred_aliases(command_aliases, inferred_commands):
            return list(alias for alias in command_aliases.keys()
                        if command_aliases[alias] in inferred_commands)

        def get_inferred_commands_and_aliases(inferred_commands,
                                              inferred_aliases):
            return distinct(inferred_commands + inferred_aliases)

        def do_store(inferred_command):
            if inferred_command in layer_alias_by_inferred_command:
                raise CommandError(
                    "Ambigous inferred command %s. " % inferred_command +
                    "Could be %s or %s" %
                    (target_path,
                     layer_alias_by_inferred_command[inferred_command]))
            layer_alias_by_inferred_command[inferred_command] = alias

        x = target_path
        x = layer = get_layer(x)
        x = inferred_commands = get_inferred_commands(layer)
        x = command_aliases = get_cmd_aliases(layer)
        x = inferred_aliases = get_inferred_aliases(command_aliases,
                                                    inferred_commands)
        x = get_inferred_commands_and_aliases(inferred_commands,
                                              inferred_aliases)
        for_each(do_store)(x)

    return layer_alias_by_inferred_command
