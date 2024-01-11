from dodo_commands.framework import ramda as R


def get_aliases(layer):
    aliases = R.path_or({}, "ROOT", "aliases")(layer)
    for cmd_name, cmd in R.path_or({}, "COMMANDS", "with_alias")(layer).items():
        aliases[cmd_name] = f"run {cmd_name}"
    return aliases
