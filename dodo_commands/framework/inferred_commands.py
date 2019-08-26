from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.alias import get_command_aliases


def get_inferred_commands(root_layer):
    layer_aliases = root_layer.get('ROOT', {}).get('layer_aliases', {})

    inferred_commands = {}
    config_io = ConfigIO()
    for layer_alias, layer_alias_target in layer_aliases.items():
        layer_filenames = config_io.glob([layer_alias_target])
        for layer_filename in layer_filenames:
            layer = config_io.load(layer_filename)
            for inferred_command in layer.get('ROOT',
                                              {}).get('inferred_commands', []):
                if inferred_command in inferred_commands:
                    raise CommandError((
                        "Ambigious inferred command: %s. Inferred layer could be "
                        + "%s or %s ") % (inferred_command,
                                          inferred_commands[inferred_command],
                                          layer_alias))
                inferred_commands[inferred_command] = layer_alias

    for alias in get_command_aliases(root_layer):
        inferred_commands[alias[0]] = inferred_commands.get(alias[1], None)

    return inferred_commands
