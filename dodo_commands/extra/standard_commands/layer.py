"""Enable or disable a layer in the configuration."""

from . import DodoCommand
from dodo_commands.framework.config import ConfigIO
from dodo_commands.framework import CommandError
import os


def _get_list_of_layers(layers, layer, value):
    result = []
    found = False
    for existing_layer in layers:
        try:
            name, variant, _ = existing_layer.split(".")
        except ValueError:
            name = None
            continue

        if name == layer:
            found = True
            result.append("%s.%s.yaml" % (name, value))
        else:
            result.append(existing_layer)

    if not found:
        result.append("%s.%s.yaml" % (layer, value))

    return result


class Command(DodoCommand):  # noqa
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
        newlayers = _get_list_of_layers(layers, layer, value)
        config['ROOT']['layers'] = newlayers
        ConfigIO().save(config)
