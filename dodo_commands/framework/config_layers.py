import os
from collections import OrderedDict

from dodo_commands.framework import ramda as R
from dodo_commands.framework.config import build_config


def layer_filename_superset(layer_filenames, config_io):
    selected_layer_by_path = OrderedDict()

    def load_layer(layer_filename):
        layer = config_io.load(layer_filename)
        selected_layer_by_path[layer_filename] = layer
        nested_layer_paths = get_nested_layer_paths(layer)
        load_layers(nested_layer_paths)

    def get_nested_layer_paths(layer):
        layer_snippet = dict(LAYERS=layer.get("LAYERS", []))
        config_snippet = build_config([layer_snippet])[0]
        return R.path_or([], "LAYERS")(config_snippet)

    def load_layers(layer_paths):
        for layer_path in config_io.glob(layer_paths):
            load_layer(layer_path)

    load_layers(layer_filenames)
    return list(selected_layer_by_path.keys())


def get_conflicts_in_layer_paths(layer_paths):
    generic_paths = {}

    def map_to_layer_path_and_parts(path):
        parts = os.path.basename(path).split(".")
        return path, parts

    def has_flavours(path, parts):
        return len(parts) == 3

    def map_to_path_and_generic_path(path, parts):
        generic_path = os.path.join(os.path.dirname(path), parts[0])
        return path, generic_path

    def is_conflict(path, generic_path):
        result = bool(generic_paths.get(generic_path, None))
        if not result:
            generic_paths[generic_path] = path
        return result

    x = layer_paths
    # [path]
    x = R.map(map_to_layer_path_and_parts)(x)
    # [(path, parts)]
    x = R.filter(R.ds(has_flavours))(x)
    # [(path, parts)]
    x = R.map(R.ds(map_to_path_and_generic_path))(x)
    # [(path, generic_path)]
    x = R.filter(R.ds(is_conflict))(x)

    return x
