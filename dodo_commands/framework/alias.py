from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.funcy import map_with, for_each, ds


def load_aliased_layers(
        config_io,
        target_path_by_alias,
):
    layer_by_alias_target_path = {}

    def get_target_paths_for_aliases():
        return target_path_by_alias.values()

    def do_check_valid_target_path(target_path):
        if '*' in target_path:
            raise CommandError("Alias target may not contain wildcards: %s" %
                               target_path)

    def add_layer(target_path):
        return target_path, config_io.load(target_path)

    def do_store(target_path, layer):
        layer_by_alias_target_path[target_path] = layer

    x = get_target_paths_for_aliases()
    # [path]
    x = for_each(do_check_valid_target_path)(x)
    # [path]
    x = map_with(add_layer)(x)
    # [(path, layer)]
    for_each(ds(do_store))(x)

    return (layer_by_alias_target_path, )
