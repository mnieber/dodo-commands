import sys

from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config import expand_keys


def load_named_layers(
    config_io,
    root_layer_config,
    metadata_by_layer_name,
):
    layer_by_target_path = {}

    def get_target_paths_and_layer_names():
        result = {}
        for layer_name, layer_metadata in metadata_by_layer_name.items():
            result[layer_name] = layer_metadata.target_path
        return result.items()

    def do_check_valid_target_path(layer_name, target_path):
        layer_path = expand_keys(root_layer_config, target_path)
        if "*" in layer_path:
            raise CommandError("Layer_name may not contain wildcards: %s" % target_path)

        if not config_io.glob([layer_path]):
            sys.stderr.write(
                "Warning: layer not found: %s. Check /LAYER_GROUPS for layer %s\n"
                % (layer_path, layer_name)
            )

    def add_layer(layer_name, target_path):
        layer_path = expand_keys(root_layer_config, target_path)
        is_found = config_io.glob([layer_path])
        layer = config_io.load(layer_path) if is_found else {}
        return layer_name, target_path, layer_path, layer

    def do_store(layer_name, target_path, layer_path, layer):
        layer_by_target_path[target_path] = layer

    x = get_target_paths_and_layer_names()
    # [layer_name, target_path]
    x = R.for_each(R.ds(do_check_valid_target_path))(x)
    # [layer_name, target_path]
    x = R.map(R.ds(add_layer))(x)
    # [(layer_name, target_path, layer)]
    R.for_each(R.ds(do_store))(x)

    return layer_by_target_path
