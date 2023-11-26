from collections import OrderedDict

from dodo_commands.framework import ramda as R
from dodo_commands.framework.config import build_config
from dodo_commands.framework.config_layers import layer_filename_superset
from dodo_commands.framework.get_metadata_by_layer_name import (
    get_metadata_by_layer_name as get_metadata_by_layer_name_,
)
from dodo_commands.framework.load_named_layers import (
    load_named_layers as load_named_layers_,
)


def load_root_layer(ctr):
    root_layer = (
        ctr.layers.config_io.load(ctr.layers.root_layer_path)
        if ctr.paths.project_dir()
        else {}
    )
    root_layer_config = build_config([root_layer])[0]

    ctr.layers.root_layer = root_layer
    ctr.layers.root_layer_config = root_layer_config


def get_metadata_by_layer_name(ctr):
    ctr.layers.metadata_by_layer_name = get_metadata_by_layer_name_(
        ctr.layers.root_layer
    )


def load_named_layers(ctr):
    layer_by_target_path = load_named_layers_(
        ctr.layers.config_io,
        ctr.layers.root_layer_config,
        ctr.layers.metadata_by_layer_name,
    )

    ctr.layers.layer_by_target_path = layer_by_target_path


def select_layers(ctr):
    all_layer_paths = layer_filename_superset(
        R.uniq([ctr.layers.root_layer_path] + ctr.command_line.target_paths),
        config_io=ctr.layers.config_io,
    )

    selected_layer_by_path = OrderedDict()
    for layer_path in all_layer_paths:
        selected_layer_by_path[layer_path] = ctr.layers.config_io.load(layer_path)

    ctr.layers.selected_layer_by_path = selected_layer_by_path
