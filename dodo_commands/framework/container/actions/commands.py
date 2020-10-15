from dodo_commands.framework.command_map import get_command_map as _get_command_map
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.container.facets import (
    Commands,
    Config,
    Layers,
    i_,
    o_,
    register,
)
from dodo_commands.framework.get_aliases import get_aliases
from dodo_commands.framework.inferred_commands import (
    get_inferred_command_map as _get_inferred_command_map,
)


# COMMANDS
@register(
    i_(Commands, "global_aliases"),
    i_(Layers, "metadata_by_layer_name"),
    i_(Layers, "layer_by_target_path"),
    o_(Commands, "layer_name_by_inferred_command"),
)
def get_inferred_command_map(
    global_aliases, metadata_by_layer_name, layer_by_target_path
):
    return dict(
        layer_name_by_inferred_command=_get_inferred_command_map(
            global_aliases,
            metadata_by_layer_name,
            layer_by_target_path,
        )
    )


# COMMANDS
@register(
    i_(Config, "config"),
    #
    o_(Commands, "aliases_from_config"),
)
def get_aliases_from_config(config):
    return dict(aliases_from_config=get_aliases(config))


# COMMANDS
@register(
    i_(Config, "config"), o_(Commands, "command_dirs"), o_(Commands, "command_map")
)
def get_command_map(config):
    command_dirs = get_command_dirs_from_config(config)
    return dict(
        command_dirs=command_dirs,
        command_map=_get_command_map(command_dirs),
    )
