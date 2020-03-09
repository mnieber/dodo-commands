from dodo_commands.framework.command_error import CommandError  # noqa
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.funcy import drill


class LayerConfig:
    def __init__(self, target_path, inferred_commands, group_name):
        self.target_path = target_path
        self.inferred_commands = inferred_commands
        self.group_name = group_name


class Layers:
    def __init__(self):
        self.config_io = ConfigIO()
        self.root_layer_path = None
        self.root_layer = None
        self.layer_by_target_path = {}
        self.selected_layer_by_path = {}

    @property
    def layer_config_by_layer_name(self):
        result = {}

        groups = drill(self.root_layer, 'LAYER_GROUPS', default={})
        for group_name, group in groups.items():
            for group_item in group:

                if isinstance(group_item, str):
                    layer_name = group_item
                    base_name = layer_name
                    inferred_commands = []
                    target_path = None
                elif isinstance(group_item, dict):
                    layer_name, layer_config = list(group_item.items())[0]
                    layer_config = layer_config or {}
                    inferred_commands = list(
                        layer_config.get('inferred_by', []))
                    target_path = layer_config.get('target_path')
                    base_name = layer_config.get('base_name', layer_name)

                target_path = target_path or "%s.%s.yaml" % (group_name,
                                                             base_name)

                layer_config = LayerConfig(target_path, inferred_commands,
                                           group_name)

                if layer_name in result:
                    prev_layer_config = result[layer_name]
                    raise CommandError(
                        "Name conlict for layer '%s' in groups '%s' and '%s'" %
                        (layer_name, prev_layer_config.group_name,
                         layer_config.group_name))

                result[layer_name] = layer_config
        return result

    @staticmethod
    def get(ctr):
        return ctr.layers


def init_layers(self, root_layer_path):
    self.root_layer_path = root_layer_path
    return self
