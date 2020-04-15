import sys

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.funcy import ds, for_each, map_with


def load_named_layers(
    config_io,
    layer_props_by_layer_name,
):
    layer_by_target_path = {}

    def get_target_paths_and_layer_names():
        result = {}
        for layer_name, layer_props in layer_props_by_layer_name.items():
            result[layer_name] = layer_props.target_path
        return result.items()

    def do_check_valid_target_path(layer_name, target_path):
        if '*' in target_path:
            raise CommandError("Layer_name may not contain wildcards: %s" %
                               target_path)

        if not config_io.glob([target_path]):
            sys.stderr.write(
                "Warning: layer not found: %s. Check /LAYER_GROUPS for layer %s\n"
                % (target_path, layer_name))

    def add_layer(layer_name, target_path):
        is_found = config_io.glob([target_path])
        layer = config_io.load(target_path) if is_found else {}
        return layer_name, target_path, layer

    def do_store(layer_name, target_path, layer):
        layer_by_target_path[target_path] = layer

    x = get_target_paths_and_layer_names()
    # [path, layer_name]
    x = for_each(ds(do_check_valid_target_path))(x)
    # [path, layer_name]
    x = map_with(ds(add_layer))(x)
    # [(path, layer_name, layer)]
    for_each(ds(do_store))(x)

    return layer_by_target_path
