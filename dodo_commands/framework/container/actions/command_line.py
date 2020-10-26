import argparse
import os

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
    i_(CommandLine, "input_args"),
    o_(CommandLine, "layer_paths_from_input_args"),
    o_(CommandLine, "is_trace"),
    o_(CommandLine, "is_help"),
    o_(CommandLine, "input_args"),
)
def parse_input_args(input_args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-L", "--layer", action="append")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--help", action="store_true")

    known_args, args = R.pipe(
        #
        R.always(input_args),
        rearrange_double_dash,
        parser.parse_known_args,
    )(None)

    return dict(
        layer_paths_from_input_args=known_args.layer or [],
        is_trace=known_args.trace,
        is_help=known_args.help,
        input_args=args,
    )


# COMMAND LINE
@register(
    i_(CommandLine, "command_prefix"),
    i_(Layers, "metadata_by_layer_name"),
    o_(CommandLine, "layer_paths_from_command_prefix"),
)
def get_layer_paths_from_command_prefix(
    command_prefix,
    metadata_by_layer_name,
):
    def map_to_path(layer_name):
        if layer_name not in metadata_by_layer_name:
            known_layer_names = metadata_by_layer_name.keys()
            raise CommandError(
                "Unknown layer: %s. Known layers: %s"
                % (layer_name, ", ".join(known_layer_names))
            )
        return metadata_by_layer_name[layer_name].target_path

    layer_names = R.uniq(R.filter(bool)(command_prefix.split(".")))
    return dict(layer_paths_from_command_prefix=R.map(map_to_path)(layer_names))


# COMMAND LINE
@register(
    i_(CommandLine, "command_name"),
    i_(Commands, "layer_name_by_inferred_command"),
    i_(Layers, "metadata_by_layer_name"),
    o_(CommandLine, "layer_paths_inferred_by_command_name"),
)
def get_layer_paths_inferred_by_command_name(
    command_name,
    layer_name_by_inferred_command,
    metadata_by_layer_name,
):
    layer_name = layer_name_by_inferred_command.get(command_name, None)
    layer_metadata = metadata_by_layer_name.get(layer_name)

    return dict(
        layer_paths_inferred_by_command_name=[layer_metadata.target_path]
        if layer_metadata
        else []
    )


# COMMAND LINE
@register(
    i_(CommandLine, "command_name"),
    i_(CommandLine, "input_args"),
    i_(Commands, "command_map"),
    i_(Commands, "aliases", alt_name="command_aliases"),
    i_(Commands, "layer_name_by_inferred_command"),
    i_(Layers, "metadata_by_layer_name"),
    i_(Layers, "layer_by_target_path"),
    o_(CommandLine, "input_args"),
)
def expand_and_autocomplete_command_name(
    command_name,
    input_args,
    command_map,
    command_aliases,
    layer_name_by_inferred_command,
    metadata_by_layer_name,
    layer_by_target_path,
):
    is_autocompleting = "_ARGCOMPLETE" in os.environ
    completed_command_name = (
        handle_arg_complete(
            command_names=list(command_map.keys()),
            inferred_command_names=list(layer_name_by_inferred_command.keys()),
            command_aliases=list(command_aliases.keys()),
            metadata_by_layer_name=metadata_by_layer_name,
            layer_by_target_path=layer_by_target_path,
        )
        if is_autocompleting
        else command_name
    )

    alias_target = command_aliases.get(completed_command_name) or completed_command_name
    new_args = alias_target.split(" ")

    return dict(
        input_args=input_args[:1] + new_args + input_args[2:],
        has_changed=not is_autocompleting and new_args != input_args[1:2],
    )
