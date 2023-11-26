from dodo_commands.framework import ramda as R
from dodo_commands.framework.global_config import load_global_config_parser


class Commands:
    def __init__(self):
        self.global_aliases = {}
        self.aliases_from_config = {}
        self.command_map = {}
        self.command_dirs = []

    @property
    def aliases(self):
        return R.merge(self.global_aliases, self.aliases_from_config)

    @staticmethod
    def get(ctr):
        return ctr.commands


def init_commands(self):
    global_config = load_global_config_parser()
    if global_config.has_section("alias"):
        self.global_aliases = dict(global_config.items("alias"))
    return self
