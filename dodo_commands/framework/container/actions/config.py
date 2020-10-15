from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config import build_config, extend_command_path
from dodo_commands.framework.config_layers import get_conflicts_in_layer_paths
from dodo_commands.framework.container.facets import Config, Layers, i_, o_, register


# CONFIG
@register(i_(Layers, "selected_layer_by_path"))
def check_conflicts_in_selected_layer_paths(selected_layer_by_path):
    conflicts = get_conflicts_in_layer_paths(selected_layer_by_path.keys())
    for path, conflicting_path in conflicts:
        raise CommandError("Conflicting layers: %s and %s" % (path, conflicting_path))
    return dict()


# CONFIG
@register(
    i_(Layers, "selected_layer_by_path"),
    i_(Layers, "metadata_by_layer_name"),
    o_(Config, "config"),
    o_(Config, "warnings"),
)
def build_from_selected_layers(
    selected_layer_by_path,
    metadata_by_layer_name,
):
    def get_selected_layers():
        return selected_layer_by_path.values()

    x = get_selected_layers()
    # [layer]
    config, warnings = build_config(x)
    config = extend_command_path(config)

    return dict(config=config, warnings=warnings)
