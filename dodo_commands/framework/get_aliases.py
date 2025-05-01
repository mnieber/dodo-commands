from dodo_commands.framework import ramda as R


def get_aliases(layer):
    aliases = R.path_or({}, "ROOT", "aliases")(layer)
    for cmd_name, cmd in R.path_or({}, "COMMANDS", "list")(layer).items():
        if cmd_name.startswith("~"):
            cmd_name = cmd_name[1:]
            aliases[cmd_name] = f"run {cmd_name}"
    return aliases
