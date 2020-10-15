import os
from collections import OrderedDict

from dodo_commands.framework import ramda as R


def layer_filename_superset(layer_filenames, config_io):
    selected_layer_by_path = OrderedDict()

    def load_layers(layer_paths):
        def map_to_layer_filenames(layer_paths):
            return config_io.glob(layer_paths)

        def map_to_filename_and_layer(layer_filename):
            return layer_filename, config_io.load(layer_filename)

        def do_store(layer_filename, layer):
            selected_layer_by_path[layer_filename] = layer

        def map_to_nested_layer_paths(layer_filename, layer):
            return R.path_or([], "LAYERS")(layer)

        def get_flat_list(list_of_lists):
            return R.uniq(R.flatten(list_of_lists))

        x = map_to_layer_filenames(layer_paths)
        # [[layer_filename]]
        x = R.map(map_to_filename_and_layer)(x)
        # [layer_filename, layer]
        x = R.for_each(R.ds(do_store))(x)
        # [layer_filename, layer]
        x = R.map(R.ds(map_to_nested_layer_paths))(x)
        # [[layer_filename]]
        x = get_flat_list(x)
        # [layer_filename, layer]
        if x:
            load_layers(x)

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
