import os

from dodo_commands.framework.handle_arg_complete import handle_arg_complete
from dodo_commands.framework.funcy import map_with
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.container.facets import (Commands, CommandLine,
                                                      Layers, map_datas, i_,
                                                      o_)


# COMMAND LINE
def action_get_expanded_layer_paths(ctr):
    def transform(
            #
            layer_aliases,
            target_path_by_alias,
    ):
        def map_to_path(alias):
            if alias not in target_path_by_alias:
                raise CommandError("Unknown layer alias: %s" % alias)
            return target_path_by_alias[alias]

        return (map_with(map_to_path)(layer_aliases), )

    return map_datas(i_(CommandLine, 'layer_aliases'),
                     i_(Layers, 'target_path_by_alias'),
                     o_(CommandLine, 'expanded_layer_paths'),
                     transform=transform)(ctr)


# COMMAND LINE
def action_get_inferred_layer_paths(ctr):
    def transform(
            #
            raw_command_name,
            layer_alias_by_inferred_command,
            target_path_by_alias):
        layer_alias = layer_alias_by_inferred_command.get(
            raw_command_name, None)
        target_path = target_path_by_alias.get(layer_alias)

        return ([target_path] if target_path else [], )

    return map_datas(i_(CommandLine, 'raw_command_name'),
                     i_(Commands, 'layer_alias_by_inferred_command'),
                     i_(Layers, 'target_path_by_alias'),
                     o_(CommandLine, 'inferred_layer_paths'),
                     transform=transform)(ctr)


# COMMAND LINE
def action_expand_and_autocomplete_command_name(ctr):
    def transform(
            #
            raw_command_name,
            input_args,
            command_map,
            aliases,
            layer_alias_by_inferred_command,
            target_path_by_alias,
    ):
        completed_command_name = (
            handle_arg_complete(command_names=list(command_map.keys()),
                                inferred_command_names=list(
                                    layer_alias_by_inferred_command.keys()),
                                command_aliases=list(aliases.keys()),
                                target_path_by_alias=target_path_by_alias)
            #
            if "_ARGCOMPLETE" in os.environ else
            #
            raw_command_name)

        alias_target = (aliases.get(completed_command_name)
                        or completed_command_name or 'help')
        new_args = alias_target.split(' ')
        command_name = new_args[0]
        input_args = input_args[:1] + new_args + input_args[2:]
        return (input_args, command_name)

    return map_datas(i_(CommandLine, 'raw_command_name'),
                     i_(CommandLine, 'input_args'),
                     i_(Commands, 'command_map'),
                     i_(Commands, 'aliases'),
                     i_(Commands, 'layer_alias_by_inferred_command'),
                     i_(Layers, 'target_path_by_alias'),
                     o_(CommandLine, 'input_args'),
                     o_(CommandLine, 'command_name'),
                     transform=transform)(ctr)
