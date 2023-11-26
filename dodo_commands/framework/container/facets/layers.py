import os

from dodo_commands.framework import ramda as R
from dodo_commands.framework.config_io import ConfigIO


class Layers:
    def __init__(self):
        self.config_io = ConfigIO()
        self.root_layer_path = None
        self.root_layer = None
        # This is a config based on root_layer (it will resolve all keys
        # that only depend on the root layer, not any other layer)
        self.root_layer_config = None
        self.layer_by_target_path = {}
        self.layer_path_by_target_path = {}
        self.selected_layer_by_path = {}
        self.metadata_by_layer_name = None

    def get_ordered_layer_paths(self):
        root_layer_path = self.config_io.glob([self.root_layer_path])[0]

        x = R.concat(
            self.selected_layer_by_path.keys(), self.layer_by_target_path.keys()
        )
        x = R.uniq(x)
        x = sorted(x, key=os.path.basename)
        x = self.config_io.glob(x)

        x = R.filter(lambda x: x != root_layer_path)(x)
        x = R.concat([root_layer_path], x)

        return x

    @staticmethod
    def get(ctr):
        return ctr.layers


def init_layers(self, root_layer_path):
    self.root_layer_path = root_layer_path
    return self
