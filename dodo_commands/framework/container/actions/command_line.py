import argparse
import os
import sys

from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.container.facets import (
    CommandLine,
    Commands,
    Layers,
    i_,
    o_,
    register,
)
from dodo_commands.framework.container.utils import rearrange_double_dash
from dodo_commands.framework.handle_arg_complete import handle_arg_complete


@register(
    i_(CommandLine, "is_running_directly_from_script"),
    i_(CommandLine, "is_help"),
    o_(CommandLine, "given_layer_paths"),
    o_(CommandLine, "is_trace"),
    o_(CommandLine, "input_args"),
)
def parse_sys_argv(is_running_directly_from_script, is_help):
    parser = argparse.ArgumentParser()
    parser.add_argument("-L", "--layer", action="append")
    parser.add_argument("--trace", action="store_true")

    known_args, args = R.pipe(
        R.always(rearrange_double_dash(sys.argv)),
        R.when(R.always(is_running_directly_from_script), R.prepend(sys.executable)),
        R.when(R.always(is_help), R.filter(lambda x: x != "--help")),
        parser.parse_known_args,
    )(None)

    return dict(
        given_layer_paths=known_args.layer or [],
        is_trace=known_args.trace,
        input_args=args,
    )


# COMMAND LINE
@register(
    i_(CommandLine, "layer_names"),
    i_(Layers, "layer_props_by_layer_name"),
    o_(CommandLine, "expanded_layer_paths"),
)
def get_expanded_layer_paths(
    layer_names, layer_props_by_layer_name,
):
    def map_to_path(layer_name):
        if layer_name not in layer_props_by_layer_name:
            known_layer_names = layer_props_by_layer_name.keys()
            raise CommandError(
                "Unknown layer: %s. Known layers: %s"
                % (layer_name, ", ".join(known_layer_names))
            )
        return layer_props_by_layer_name[layer_name].target_path

    return dict(expanded_layer_paths=R.map(map_to_path)(layer_names))


# COMMAND LINE
@register(
    i_(CommandLine, "command_name"),
    i_(Commands, "layer_name_by_inferred_command"),
    i_(Layers, "layer_props_by_layer_name"),
    o_(CommandLine, "inferred_layer_paths"),
)
def get_inferred_layer_paths(
    command_name, layer_name_by_inferred_command, layer_props_by_layer_name,
):
    layer_name = layer_name_by_inferred_command.get(command_name, None)
    layer_props = layer_props_by_layer_name.get(layer_name)

    return dict(inferred_layer_paths=[layer_props.target_path] if layer_props else [])


# COMMAND LINE
@register(
    i_(CommandLine, "command_name"),
    i_(CommandLine, "input_args"),
    i_(Commands, "command_map"),
    i_(Commands, "aliases", alt_name="command_aliases"),
    i_(Commands, "layer_name_by_inferred_command"),
    i_(Layers, "layer_props_by_layer_name"),
    i_(Layers, "layer_by_target_path"),
    o_(CommandLine, "input_args"),
    o_(CommandLine, "more_given_layer_paths"),
)
def expand_and_autocomplete_command_name(
    command_name,
    input_args,
    command_map,
    command_aliases,
    layer_name_by_inferred_command,
    layer_props_by_layer_name,
    layer_by_target_path,
):
    completed_command_name = (
        handle_arg_complete(
            command_names=list(command_map.keys()),
            inferred_command_names=list(layer_name_by_inferred_command.keys()),
            command_aliases=list(command_aliases.keys()),
            layer_props_by_layer_name=layer_props_by_layer_name,
            layer_by_target_path=layer_by_target_path,
        )
        if "_ARGCOMPLETE" in os.environ
        else command_name
    )

    alias_target = (
        command_aliases.get(completed_command_name) or completed_command_name or "help"
    )

    new_args = alias_target.split(" ")
    if "--" in new_args and "--" in input_args:
        pos_in_input_args = input_args.index("--")
        pos_in_new_args = new_args.index("--")
        new_args = (
            new_args[:pos_in_new_args]
            + input_args[pos_in_input_args + 1 :]
            + new_args[pos_in_new_args:]
        )
        input_args = input_args[:pos_in_input_args]

    parser = argparse.ArgumentParser()
    parser.add_argument("-L", "--layer", action="append")
    known_args, new_args = parser.parse_known_args(new_args)

    return dict(
        input_args=input_args[:1] + new_args + input_args[2:],
        more_given_layer_paths=known_args.layer or [],
    )

