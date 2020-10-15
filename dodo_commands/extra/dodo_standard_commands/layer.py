import os
import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.framework.config_io import ConfigIO


def _args():
    parser = ArgumentParser(
        description="Enable or disable a layer in the configuration."
    )
    parser.add_argument("layer", nargs="?", default=False)
    parser.add_argument("value", nargs="?", default=False)
    parser.add_argument("--force", action="store_true")
    args = Dodo.parse_args(parser)
    return args


def _layer_name(x):
    try:
        return x.split(".")[0]
    except ValueError:
        return None


def _update_list_of_layers(layers, new_layer_name, new_layer_variant):
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


def _layer_value(layers, layer):
    for l in layers:
        if l.startswith(layer + "."):
            try:
                parts = l.split(".")
                if len(parts) == 3:
                    return parts[1]
            except ValueError:
                pass
    return None


def _layers(config, filter_abs_paths=False):
    layers = config.get("LAYERS", [])
    if filter_abs_paths:
        layers = [
            x
            for x in layers
            if not os.path.exists(os.path.expanduser(os.path.dirname(x)))
        ]
    return layers


if Dodo.is_main(__name__, safe=False):
    args = _args()
    config = ConfigIO().load()

    if args.layer == False:  # noqa
        filtered_layers = _layers(config, filter_abs_paths=True)
        for layer in filtered_layers:
            name = _layer_name(layer)
            if name:
                value = _layer_value(filtered_layers, name)
                if value:
                    print(name + ": " + _layer_value(filtered_layers, name))
        sys.exit(0)

    layers = _layers(config)
    if args.value == False:  # noqa
        print(_layer_value(layers, args.layer))
        sys.exit(0)

    layer_file = os.path.join(
        Dodo.get("/ROOT/config_dir"), "%s.%s.yaml" % (args.layer, args.value)
    )

    if not args.force and not os.path.exists(layer_file):
        raise CommandError("Layer file %s does not exist" % layer_file)

    config["LAYERS"] = _update_list_of_layers(layers, args.layer, args.value)
    ConfigIO().save(config)
