from collections import OrderedDict

from dodo_commands.framework import ramda as R
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.container.container import Container
from dodo_commands.framework.container.facets import (
    CommandLine,
    Layers,
    i_,
    o_,
    register,
)
from dodo_commands.framework.get_metadata_by_layer_name import (
    get_metadata_by_layer_name as _get_metadata_by_layer_name,
)
from dodo_commands.framework.load_named_layers import (
    load_named_layers as _load_named_layers,
)


# LAYERS
@register(
    i_(Container, "paths"),
    i_(Layers, "config_io"),
    i_(Layers, "root_layer_path"),
    #
    o_(Layers, "root_layer"),
)
def load_root_layer(paths, config_io, root_layer_path):
    return dict(
        root_layer=config_io.load(root_layer_path) if paths.project_dir() else {}
    )


# LAYERS
@register(
    i_(Layers, "root_layer"),
    #
    o_(Layers, "metadata_by_layer_name"),
)
def get_metadata_by_layer_name(root_layer):
    return dict(metadata_by_layer_name=_get_metadata_by_layer_name(root_layer))


# LAYERS
@register(
    i_(Layers, "config_io"),
    i_(Layers, "metadata_by_layer_name"),
    o_(Layers, "layer_by_target_path"),
)
def load_named_layers(config_io, metadata_by_layer_name):
    return dict(
        layer_by_target_path=_load_named_layers(
            config_io,
            metadata_by_layer_name,
        )
    )


# LAYERS
@register(
    i_(Layers, "config_io"),
    i_(Layers, "root_layer_path"),
    i_(Layers, "root_layer"),
    i_(CommandLine, "layer_paths", alt_name="command_line_layer_paths"),
    o_(Layers, "selected_layer_by_path"),
)
def select_layers(
    config_io,
    root_layer_path,
    root_layer,
    command_line_layer_paths,
):
    all_layer_paths = layer_filename_superset(
        R.uniq([root_layer_path] + command_line_layer_paths), config_io=config_io
    )

    selected_layer_by_path = OrderedDict()
    for layer_path in all_layer_paths:
        selected_layer_by_path[layer_path] = config_io.load(layer_path)
    return dict(selected_layer_by_path=selected_layer_by_path)
