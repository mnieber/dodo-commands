import os
from argparse import ArgumentParser

from dodo_commands.dependencies.get import argcomplete
from dodo_commands.framework import ramda as R
from dodo_commands.framework.config_layers import get_conflicts_in_layer_paths
from dodo_commands.framework.get_aliases import get_aliases


def handle_arg_complete(
    command_names,
    command_aliases,
    metadata_by_layer_name,
    layer_by_target_path,
):
    def get_args():
        return os.environ["COMP_LINE"].split()

    def get_prefix_and_command(args):
        return R.split(args[1].rfind(".") + 1)(args[1])

    input_args = get_args()
    full_command_name = input_args[1]
    # [arg]
    (command_prefix, command_name) = get_prefix_and_command(input_args)

    def get_used_layer_names(command_prefix):
        return [x for x in command_prefix.split(".") if x in metadata_by_layer_name]

    used_layer_names = get_used_layer_names(command_prefix)

    def get_commands():
        more_aliases = []
        for layer_name in used_layer_names:
            layer_metadata = metadata_by_layer_name[layer_name]
            layer = layer_by_target_path[layer_metadata.target_path]
            more_aliases.extend(get_aliases(layer).keys())

        return R.uniq(command_names + command_aliases + more_aliases)

    def get_choices(commands):
        return [(command_prefix + x) for x in commands]

    commands = get_commands()  # [command_name]
    choices = get_choices(commands)  # [choice]

    def get_possible_layer_names():
        return metadata_by_layer_name.keys()

    def is_already_used(layer_name):
        return layer_name in used_layer_names

    def is_conflicting(layer_name):
        used_layer_metadata = R.map(metadata_by_layer_name)(used_layer_names)
        used_layer_paths = [x.target_path for x in used_layer_metadata]

        layer_path = metadata_by_layer_name[layer_name].target_path
        return get_conflicts_in_layer_paths(used_layer_paths + [layer_path])

    def map_to_choices(layer_name):
        return [command_prefix + layer_name + "." + x for x in commands]

    x = get_possible_layer_names()
    # [layer_name]
    x = R.remove_if(is_already_used)(x)
    # [layer_name]
    x = R.remove_if(is_conflicting)(x)
    # [layer_name]
    new_choices = R.map(map_to_choices)(x)
    # [[new_choice]]
    choices += R.flatten(new_choices)

    if full_command_name not in choices:
        parser = ArgumentParser()
        parser.add_argument("command", choices=choices)
        argcomplete.autocomplete(parser)

    # Hack to make argcomplete work with zsh
    os.environ["COMP_POINT"] = str(len(os.environ["COMP_LINE"]))

    return command_name
