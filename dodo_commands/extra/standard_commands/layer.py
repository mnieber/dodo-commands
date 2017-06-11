"""Enable or disable a layer in the configuration."""

from . import DodoCommand
from dodo_commands.framework.config import ConfigIO
from dodo_commands.framework import CommandError
import os


def _update_list_of_layers(layers, new_layer_name, new_layer_variant):
    def _layer_name(x):
        # layers with a prefix path are not named
        if os.path.dirname(x):
            return None
        try:
            return x.split(".")[0]
        except ValueError:
            return None

    def _new_layer():
        return "%s.%s.yaml" % (new_layer_name, new_layer_variant)

    result = []
    found = False
    for layer in layers:
        if _layer_name(layer) == new_layer_name:
            found = True
            result.append(_new_layer())
        else:
            result.append(layer)
    if not found:
        result.append(_new_layer())

    return result


class Command(DodoCommand):  # noqa
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('layer')
        parser.add_argument('value')
        parser.add_argument('--force', action="store_true")

    def handle_imp(self, layer, value, force, **kwargs):  # noqa
        layer_file = os.path.join(
            self.get_config("/ROOT/res_dir"),
            self.get_config("/ROOT/layer_dir", ""),
            "%s.%s.yaml" % (layer, value)
        )

        if not force and not os.path.exists(layer_file):
            raise CommandError("Layer file %s does not exist" % layer_file)

        config = ConfigIO().load(load_layers=False)
        layers = config.get('ROOT', {}).get('layers', [])
        newlayers = _update_list_of_layers(layers, layer, value)
        config['ROOT']['layers'] = newlayers
        ConfigIO().save(config)
