from collections import OrderedDict

from dodo_commands.dependencies.get import funcy
from dodo_commands.framework.alias import load_named_layers
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.container.facets import (CommandLine, Layers, i_,
                                                      map_datas, o_)

distinct = funcy.distinct


# LAYERS
def action_load_root_layer(ctr):
    def transform(
        config_io,
        root_layer_path,
    ):
        if ctr.paths.project_dir():
            return (config_io.load(root_layer_path), )
        return ({}, )

    return map_datas(i_(Layers, 'config_io'),
                     i_(Layers, 'root_layer_path'),
                     o_(Layers, 'root_layer'),
                     transform=transform)(ctr)


# LAYERS
def action_load_named_layers(ctr):
    def transform(
        config_io,
        layer_props_by_layer_name,
    ):
        layer_by_target_path = load_named_layers(
            config_io,
            layer_props_by_layer_name,
        )
        return (layer_by_target_path, )

    return map_datas(i_(Layers, 'config_io'),
                     i_(Layers, 'layer_props_by_layer_name'),
                     o_(Layers, 'layer_by_target_path'),
                     transform=transform)(ctr)


# LAYERS
def action_select_layers(ctr):
    def transform(
        config_io,
        root_layer_path,
        root_layer,
        command_line_layer_paths,
    ):
        all_layer_paths = layer_filename_superset(
            distinct([root_layer_path] + command_line_layer_paths),
            config_io=config_io)

        selected_layer_by_path = OrderedDict()
        for layer_path in all_layer_paths:
            selected_layer_by_path[layer_path] = config_io.load(layer_path)
        return (selected_layer_by_path, )

    return map_datas(i_(Layers, 'config_io'),
                     i_(Layers, 'root_layer_path'),
                     i_(Layers, 'root_layer'),
                     i_(CommandLine,
                        'layer_paths',
                        alt_name='command_line_layer_paths'),
                     o_(Layers, 'selected_layer_by_path'),
                     transform=transform)(ctr)
