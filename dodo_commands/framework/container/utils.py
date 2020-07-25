import os

from dodo_commands.framework import ramda as R


def get_ordered_layer_paths(ctr):
    root_layer_path = ctr.layers.config_io.glob([ctr.layers.root_layer_path])[0]

    x = R.concat(
        ctr.layers.selected_layer_by_path.keys(), ctr.layers.layer_by_target_path.keys()
    )
    x = R.uniq(x)
    x = sorted(x, key=os.path.basename)
    x = ctr.layers.config_io.glob(x)

    x = R.filter(lambda x: x != root_layer_path)(x)
    x = R.concat([root_layer_path], x)

    return x
