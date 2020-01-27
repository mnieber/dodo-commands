import os
import sys

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.funcy import map_with, for_each, ds


def load_aliased_layers(
    config_io,
    target_path_by_alias,
):
    layer_by_alias_target_path = {}

    def get_target_paths_and_aliases():
        return target_path_by_alias.items()

    def do_check_valid_target_path(alias, target_path):
        if '*' in target_path:
            raise CommandError("Alias target may not contain wildcards: %s" %
                               target_path)

        if not config_io.glob([target_path]):
            sys.stderr.write(
                "Warning: layer not found: %s. Check /ROOT/layer_aliases/%s\n"
                % (target_path, alias))

    def add_layer(alias, target_path):
        is_found = config_io.glob([target_path])
        layer = config_io.load(target_path) if is_found else {}
        return alias, target_path, layer

    def do_store(alias, target_path, layer):
        layer_by_alias_target_path[target_path] = layer

    x = get_target_paths_and_aliases()
    # [path, alias]
    x = for_each(ds(do_check_valid_target_path))(x)
    # [path, alias]
    x = map_with(ds(add_layer))(x)
    # [(path, alias, layer)]
    for_each(ds(do_store))(x)

    return (layer_by_alias_target_path, )
