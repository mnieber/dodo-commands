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


# if there are two args that equal "--" then we assume that everything
# behind the second instance of "--" is a part of the "left side" of the
# command line
def rearrange_double_dash(args):
    left, rest = R.split_when(R.equals("--"), args)
    middle, right = [], []
    if rest:
        middle, rest = R.split_when(R.equals("--"), rest[1:])
        if rest:
            right, rest = R.split_when(R.equals("--"), rest[1:])
    return left + right + (R.prepend("--")(middle) if middle else [])
