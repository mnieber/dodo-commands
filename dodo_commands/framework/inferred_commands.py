from dodo_commands.dependencies.get import funcy
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.funcy import drill, for_each

distinct, merge = funcy.distinct, funcy.merge


def get_inferred_command_map(
    global_aliases,
    layer_props_by_layer_name,
    layer_by_target_path,
):
    layer_name_by_inferred_command = {}

    for layer_name, layer_props in layer_props_by_layer_name.items():

        def get_layer(layer_props):
            return layer_by_target_path[layer_props.target_path]

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
            if inferred_command in layer_name_by_inferred_command:
                raise CommandError(
                    "Ambigous inferred command %s. " % inferred_command +
                    "Could be %s or %s" %
                    (layer_props.target_path,
                     layer_name_by_inferred_command[inferred_command]))
            layer_name_by_inferred_command[inferred_command] = layer_name

        x = layer_props
        x = layer = get_layer(x)
        x = command_aliases = get_cmd_aliases(layer)
        x = inferred_aliases = get_inferred_aliases(
            command_aliases, layer_props.inferred_commands)
        x = get_inferred_commands_and_aliases(layer_props.inferred_commands,
                                              inferred_aliases)
        for_each(do_store)(x)

    return layer_name_by_inferred_command
