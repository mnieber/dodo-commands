from funcy.py2 import distinct
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.alias import load_aliased_layers
from dodo_commands.framework.container.facets import Layers, CommandLine, map_datas, i_, o_


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
def action_load_aliased_layers(ctr):
    def transform(
            config_io,
            target_path_by_alias,
    ):
        layer_by_alias_target_path = load_aliased_layers(
            config_io,
            target_path_by_alias,
        )
        return (layer_by_alias_target_path, )

    return map_datas(i_(Layers, 'config_io'),
                     i_(Layers, 'target_path_by_alias'),
                     o_(Layers, 'layer_by_alias_target_path'),
                     transform=load_aliased_layers)(ctr)


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

        selected_layer_by_path = {}
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
