from dodo_commands.framework.command_map import get_command_map as _get_command_map
from dodo_commands.framework.command_path import get_command_dirs_from_config
from dodo_commands.framework.get_aliases import get_aliases


def get_aliases_from_config(ctr):
    ctr.commands.aliases_from_config = get_aliases(ctr.config.config)


def get_command_map(ctr):
    command_dirs = get_command_dirs_from_config(ctr.config.config)

    ctr.commands.command_dirs = command_dirs
    ctr.commands.command_map = _get_command_map(command_dirs)
