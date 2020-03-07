import os
from argparse import ArgumentParser

import argcomplete
from dodo_commands.framework.config_layers import get_conflicts_in_layer_paths
from dodo_commands.framework.funcy import (keep_truthy, map_with, remove_if,
                                           str_split_at)
from funcy.py2 import distinct, flatten


def handle_arg_complete(command_names, inferred_command_names, command_aliases,
                        target_path_by_layer_name):
    def get_args():
        return os.environ['COMP_LINE'].split()

    def get_prefix_and_command(args):
        return str_split_at(args[1], args[1].rfind('.') + 1)

    input_args = get_args()
    full_command_name = input_args[1]
    # [arg]
    (command_prefix, command_name) = get_prefix_and_command(input_args)

    def get_used_layer_names(command_prefix):
        return keep_truthy()(command_prefix.split('.'))

    used_layer_names = get_used_layer_names(command_prefix)

    def get_commands():
        return distinct(command_names + inferred_command_names +
                        command_aliases)

    def get_choices(commands):
        return [(command_prefix + x) for x in commands]

    commands = get_commands()  # [command_name]
    choices = get_choices(commands)  # [choice]

    def get_possible_layer_names():
        return target_path_by_layer_name.keys()

    def is_already_used(layer_name):
        return layer_name in used_layer_names

    def is_conflicting(layer_name):
        used_layer_paths = map_with(target_path_by_layer_name)(
            used_layer_names)
        layer_path = target_path_by_layer_name[layer_name]
        return get_conflicts_in_layer_paths(used_layer_paths + [layer_path])

    def map_to_choices(layer_name):
        return [command_prefix + layer_name + "." + x for x in commands]

    x = get_possible_layer_names()
    # [layer_name]
    x = remove_if(is_already_used)(x)
    # [layer_name]
    x = remove_if(is_conflicting)(x)
    # [layer_name]
    new_choices = map_with(map_to_choices)(x)
    # [[new_choice]]
    choices += flatten(new_choices)

    if full_command_name not in choices:
        parser = ArgumentParser()
        parser.add_argument('command', choices=choices)
        argcomplete.autocomplete(parser)

    os.environ['COMP_LINE'] = ' '.join(input_args[:1] + input_args[2:])
    os.environ['COMP_POINT'] = str(
        int(os.environ['COMP_POINT']) - (len(full_command_name) + 1))

    return command_name
