from dodo_commands.framework.config import build_config, extend_command_path
from dodo_commands.framework.config_layers import get_conflicts_in_layer_paths
from dodo_commands.framework.container.facets import Layers, Config, map_datas, i_, o_
from dodo_commands.framework.command_error import CommandError


# CONFIG
def action_check_conflicts_in_selected_layer_paths(ctr):
    def transform(selected_layer_by_path):
        conflicts = get_conflicts_in_layer_paths(selected_layer_by_path.keys())
        for path, conflicting_path in conflicts:
            raise CommandError("Conflicting layers: %s and %s" %
                               (path, conflicting_path))
        return tuple()

    return map_datas(i_(Layers, 'selected_layer_by_path'),
                     transform=transform)(ctr)


# CONFIG
def action_build_from_selected_layers(ctr):
    def transform(
        #
        selected_layer_by_path):
        def get_selected_layers():
            return selected_layer_by_path.values()

        def _build_config(layers):
            return build_config(layers)

        x = get_selected_layers()
        # [layer]
        config = build_config(x)
        config = extend_command_path(config)

        return (config, )

    return map_datas(i_(Layers, 'selected_layer_by_path'),
                     o_(Config, 'config'),
                     transform=transform)(ctr)