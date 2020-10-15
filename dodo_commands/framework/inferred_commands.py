from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.get_aliases import get_aliases


def get_inferred_command_map(
    global_aliases,
    metadata_by_layer_name,
    layer_by_target_path,
):
    layer_name_by_inferred_command = {}

    for layer_name, layer_metadata in metadata_by_layer_name.items():

        def get_layer(layer_metadata):
            return layer_by_target_path[layer_metadata.target_path]

        def get_cmd_aliases(layer):
            command_aliases = get_aliases(layer)
            for alias, target in global_aliases.items():
                if alias in command_aliases:
                    raise CommandError(
                        "Ambigous command alias %s, could be %s or %s"
                        % (alias, target, command_aliases[alias])
                    )
            return R.merge(command_aliases, global_aliases)

        def get_inferred_aliases(command_aliases, inferred_commands):
            return list(
                alias
                for alias in command_aliases.keys()
                if command_aliases[alias] in inferred_commands
            )

        def get_inferred_commands_and_aliases(inferred_commands, inferred_aliases):
            return R.uniq(inferred_commands + inferred_aliases)

        def do_store(inferred_command):
            if inferred_command in layer_name_by_inferred_command:
                raise CommandError(
                    "Ambigous inferred command %s. " % inferred_command
                    + "Could be %s or %s"
                    % (
                        layer_metadata.target_path,
                        layer_name_by_inferred_command[inferred_command],
                    )
                )
            layer_name_by_inferred_command[inferred_command] = layer_name

        x = layer_metadata
        x = layer = get_layer(x)
        x = command_aliases = get_cmd_aliases(layer)
        x = inferred_aliases = get_inferred_aliases(
            command_aliases, layer_metadata.inferred_commands
        )
        x = get_inferred_commands_and_aliases(
            layer_metadata.inferred_commands, inferred_aliases
        )
        R.for_each(do_store)(x)

    return layer_name_by_inferred_command
