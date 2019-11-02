from dodo_commands.framework.funcy import drill
from dodo_commands.framework.container.facets import (Commands, Layers, Config,
                                                      map_datas, i_, o_)
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.inferred_commands import get_inferred_command_map


# COMMANDS
def action_get_inferred_command_map(ctr):
    def transform(
            global_aliases,
            target_path_by_alias,
            layer_by_alias_target_path,
    ):
        layer_alias_by_inferred_command = get_inferred_command_map(
            global_aliases,
            target_path_by_alias,
            layer_by_alias_target_path,
        )
        return (layer_alias_by_inferred_command, )

    return map_datas(i_(Commands, 'global_aliases'),
                     i_(Layers, 'target_path_by_alias'),
                     i_(Layers, 'layer_by_alias_target_path'),
                     o_(Commands, 'layer_alias_by_inferred_command'),
                     transform=transform)(ctr)


# COMMANDS
def action_get_aliases_from_config(ctr):
    def transform(config):
        return (drill(config, 'ROOT', 'aliases', default={}), )

    return map_datas(i_(Config, 'config'),
                     o_(Commands, 'aliases_from_config'),
                     transform=transform)(ctr)


# COMMANDS
def action_get_command_map(ctr):
    def transform(config):
        command_dirs = get_command_dirs_from_config(config)
        command_map = get_command_map(command_dirs)
        return (command_dirs, command_map)

    return map_datas(i_(Config, 'config'),
                     o_(Commands, 'command_dirs'),
                     o_(Commands, 'command_map'),
                     transform=transform)(ctr)
