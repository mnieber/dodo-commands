import argparse
import os
import shlex

from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.handle_arg_complete import handle_arg_complete


def parse_input_args(ctr):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-L", "--layer", action="append")
    parser.add_argument("-D", "--decorator", action="append")
    parser.add_argument("--env", action="append")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--help", action="store_true")
    parser.add_argument("--cwd")

    known_args, args = parser.parse_known_args(ctr.command_line.input_args)

    ctr.command_line.layer_paths_from_input_args = known_args.layer or []
    ctr.command_line.decorators_from_input_args = known_args.decorator or []
    ctr.command_line.env_vars_from_input_args = known_args.env or []
    ctr.command_line.cwd = known_args.cwd or None
    ctr.command_line.is_trace = known_args.trace
    ctr.command_line.is_help = known_args.help
    ctr.command_line.input_args = args


def get_layer_paths_from_command_prefix(ctr):
    def map_to_path(layer_name):
        if layer_name not in ctr.layers.metadata_by_layer_name:
            known_layer_names = ctr.layers.metadata_by_layer_name.keys()
            raise CommandError(
                "Unknown layer: %s. Known layers: %s"
                % (layer_name, ", ".join(known_layer_names))
            )
        return ctr.layers.metadata_by_layer_name[layer_name].target_path

    layer_names = R.uniq(R.filter(bool)(ctr.command_line.command_prefix.split(".")))
    layer_paths_from_command_prefix = (
        R.map(map_to_path)(layer_names)
        or ctr.command_line.layer_paths_from_command_prefix
    )

    ctr.command_line.layer_paths_from_command_prefix = layer_paths_from_command_prefix


def expand_and_autocomplete_command_name(ctr):
    is_autocompleting = "_ARGCOMPLETE" in os.environ
    completed_command_name = (
        handle_arg_complete(
            command_names=list(ctr.commands.command_map.keys()),
            command_aliases=list(ctr.commands.aliases.keys()),
            metadata_by_layer_name=ctr.layers.metadata_by_layer_name,
            layer_by_target_path=ctr.layers.layer_by_target_path,
        )
        if is_autocompleting
        else ctr.command_line.command_name
    )

    alias_target = ctr.commands.aliases.get(completed_command_name)
    new_args = (
        shlex.split(alias_target) if alias_target else ctr.command_line.input_args[1:2]
    )

    ctr.command_line.input_args = (
        ctr.command_line.input_args[:1] + new_args + ctr.command_line.input_args[2:]
    )
    return not is_autocompleting and new_args != ctr.command_line.input_args[1:2]
