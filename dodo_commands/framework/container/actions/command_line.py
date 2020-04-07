import argparse
import os

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.container.facets import (CommandLine, Commands,
                                                      Layers, i_, map_datas,
                                                      o_)
from dodo_commands.framework.funcy import map_with
from dodo_commands.framework.handle_arg_complete import handle_arg_complete


# COMMAND LINE
def action_get_expanded_layer_paths(ctr):
    def transform(
        #
        layer_names,
        layer_props_by_layer_name,
    ):
        def map_to_path(layer_name):
            if layer_name not in layer_props_by_layer_name:
                known_layer_names = layer_props_by_layer_name.keys()
                raise CommandError("Unknown layer: %s. Known layers: %s" %
                                   (layer_name, ", ".join(known_layer_names)))
            return layer_props_by_layer_name[layer_name].target_path

        return (map_with(map_to_path)(layer_names), )

    return map_datas(i_(CommandLine, 'layer_names'),
                     i_(Layers, 'layer_props_by_layer_name'),
                     o_(CommandLine, 'expanded_layer_paths'),
                     transform=transform)(ctr)


# COMMAND LINE
def action_get_inferred_layer_paths(ctr):
    def transform(
        #
        raw_command_name,
        layer_name_by_inferred_command,
        layer_props_by_layer_name):
        layer_name = layer_name_by_inferred_command.get(raw_command_name, None)
        layer_props = layer_props_by_layer_name.get(layer_name)

        return ([layer_props.target_path] if layer_props else [], )

    return map_datas(i_(CommandLine, 'raw_command_name'),
                     i_(Commands, 'layer_name_by_inferred_command'),
                     i_(Layers, 'layer_props_by_layer_name'),
                     o_(CommandLine, 'inferred_layer_paths'),
                     transform=transform)(ctr)


# COMMAND LINE
def action_expand_and_autocomplete_command_name(ctr):
    def transform(
        #
        raw_command_name,
        input_args,
        command_map,
        command_aliases,
        layer_name_by_inferred_command,
        layer_props_by_layer_name,
    ):
        completed_command_name = (
            handle_arg_complete(
                command_names=list(command_map.keys()),
                inferred_command_names=list(
                    layer_name_by_inferred_command.keys()),
                command_aliases=list(command_aliases.keys()),
                layer_props_by_layer_name=layer_props_by_layer_name)
            #
            if "_ARGCOMPLETE" in os.environ else
            #
            raw_command_name)

        alias_target = (command_aliases.get(completed_command_name)
                        or completed_command_name or 'help')

        new_args = alias_target.split(' ')

        parser = argparse.ArgumentParser()
        parser.add_argument('-L', '--layer', action='append')
        known_args, new_args = parser.parse_known_args(new_args)

        command_name = new_args[0]
        input_args = input_args[:1] + new_args + input_args[2:]
        return (input_args, command_name, known_args.layer or [])

    return map_datas(i_(CommandLine, 'raw_command_name'),
                     i_(CommandLine, 'input_args'),
                     i_(Commands, 'command_map'),
                     i_(Commands, 'aliases', alt_name='command_aliases'),
                     i_(Commands, 'layer_name_by_inferred_command'),
                     i_(Layers, 'layer_props_by_layer_name'),
                     o_(CommandLine, 'input_args'),
                     o_(CommandLine, 'command_name'),
                     o_(CommandLine, 'more_given_layer_paths'),
                     transform=transform)(ctr)
