from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config import build_config, extend_command_path
from dodo_commands.framework.config_layers import get_conflicts_in_layer_paths


def check_conflicts_in_selected_layer_paths(ctr):
    conflicts = get_conflicts_in_layer_paths(ctr.layers.selected_layer_by_path.keys())
    for path, conflicting_path in conflicts:
        raise CommandError("Conflicting layers: %s and %s" % (path, conflicting_path))


def build_from_selected_layers(ctr):
    def get_selected_layers():
        return ctr.layers.selected_layer_by_path.values()

    x = get_selected_layers()
    config, warnings = build_config(x)
    config = extend_command_path(config)

    ctr.config.config = config
    ctr.config.warnings = warnings
