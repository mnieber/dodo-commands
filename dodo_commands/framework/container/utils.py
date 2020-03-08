import os

from dodo_commands.dependencies.get import funcy
from dodo_commands.framework.funcy import remove_if

concat, distinct = funcy.concat, funcy.distinct


def get_ordered_layer_paths(ctr):
    root_layer_path = ctr.layers.config_io.glob([ctr.layers.root_layer_path
                                                 ])[0]

    x = concat(ctr.layers.selected_layer_by_path.keys(),
               ctr.layers.layer_by_target_path.keys())
    x = distinct(x)
    x = sorted(x, key=os.path.basename)
    x = ctr.layers.config_io.glob(x)

    x = remove_if(lambda x: x == root_layer_path)(x)
    x = concat([root_layer_path], x)

    return x
