import sys

from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError


def load_named_layers(
    config_io,
    metadata_by_layer_name,
):
    layer_by_target_path = {}

    def get_target_paths_and_layer_names():
        result = {}
        for layer_name, layer_metadata in metadata_by_layer_name.items():
            result[layer_name] = layer_metadata.target_path
        return result.items()

    def do_check_valid_target_path(layer_name, target_path):
        if "*" in target_path:
            raise CommandError("Layer_name may not contain wildcards: %s" % target_path)

        if not config_io.glob([target_path]):
            sys.stderr.write(
                "Warning: layer not found: %s. Check /LAYER_GROUPS for layer %s\n"
                % (target_path, layer_name)
            )

    def add_layer(layer_name, target_path):
        is_found = config_io.glob([target_path])
        layer = config_io.load(target_path) if is_found else {}
        return layer_name, target_path, layer

    def do_store(layer_name, target_path, layer):
        layer_by_target_path[target_path] = layer

    x = get_target_paths_and_layer_names()
    # [path, layer_name]
    x = R.for_each(R.ds(do_check_valid_target_path))(x)
    # [path, layer_name]
    x = R.map(R.ds(add_layer))(x)
    # [(path, layer_name, layer)]
    R.for_each(R.ds(do_store))(x)

    return layer_by_target_path
