from dodo_commands.framework import ramda as R


def get_aliases(layer):
    return R.path_or({}, "ROOT", "aliases")(layer)
