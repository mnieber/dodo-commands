from dodo_commands.framework.command_error import CommandError  # noqa
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.funcy import drill


class Layers:
    def __init__(self):
        self.config_io = ConfigIO()
        self.root_layer_path = None
        self.root_layer = None
        self.layer_by_target_path = {}
        self.selected_layer_by_path = {}

    @property
    def target_path_by_layer_name(self):
        return drill(self.root_layer, 'ROOT', 'layer_names', default={})

    @staticmethod
    def get(ctr):
        return ctr.layers


def init_layers(self, root_layer_path):
    self.root_layer_path = root_layer_path
    return self
