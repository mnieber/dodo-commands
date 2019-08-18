from fnmatch import fnmatch
import os

from dodo_commands.framework.config_io import ConfigIO


def get_layers(base_config=None, extra_layers=None):
    config_io = ConfigIO()
    layer_filenames = []
    base_config = base_config or config_io.load() or {}

    for pattern in base_config.get('ROOT', {}).get('layers', []):
        filenames = config_io.glob([pattern])
        if not filenames:
            print("Warning, no layers found for pattern: %s" % pattern)
        layer_filenames.extend(filenames)

    for extra_layer_filename in config_io.glob(extra_layers or []):
        # Remove layers in the same group, because by definition
        # we should not use both foo.bar.yaml and foo.baz.yaml.
        parts = os.path.basename(extra_layer_filename).split('.')
        if len(parts) == 3:
            pattern = os.path.join(os.path.dirname(extra_layer_filename),
                                   parts[0] + '.*.*')
            layer_filenames = [
                x for x in layer_filenames if not fnmatch(x, pattern)
            ]

        if extra_layer_filename not in layer_filenames:
            layer_filenames.append(extra_layer_filename)

    return layer_filenames
