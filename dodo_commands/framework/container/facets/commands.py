from dodo_commands.dependencies.get import funcy
from dodo_commands.framework.global_config import load_global_config_parser

merge = funcy.merge


class Commands:
    def __init__(self):
        self.layer_name_by_inferred_command = {}
        self.global_aliases = {}
        self.aliases_from_config = {}
        self.command_map = {}
        self.command_dirs = []

    @property
    def aliases(self):
        return merge(self.global_aliases, self.aliases_from_config)

    @staticmethod
    def get(ctr):
        return ctr.commands


def init_commands(self):
    global_config = load_global_config_parser()
    if global_config.has_section('alias'):
        self.global_aliases = dict(global_config.items('alias'))
    return self
