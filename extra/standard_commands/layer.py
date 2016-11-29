"""Enable or disable a layer in the configuration."""

from . import DodoCommand
import sys
from dodo_commands.framework.config import ConfigIO


def _get_list_of_layers(layers, layer, value):
    newlayers = []
    found = False
    for existing_layer in layers:
        name, variant, _ = existing_layer.split(".")
        if name == layer:
            found = True
            newlayers.append("%s.%s.yaml" % (name, value))
        else:
            newlayers.append(existing_layer)

    return newlayers, found


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('layer')
        parser.add_argument('value')

    def handle_imp(self, layer, value, **kwargs):  # noqa
        config = ConfigIO().load(load_layers=False)
        layers = config.get('ROOT', {}).get('layers', [])
        newlayers, found = _get_list_of_layers(layers, layer, value)
        if found:
            config['ROOT']['layers'] = newlayers
            ConfigIO().save(config)
        else:
            sys.stderr.write(
                "Warning, skipped non-existing layer %s in ROOT\n" % layer
            )
