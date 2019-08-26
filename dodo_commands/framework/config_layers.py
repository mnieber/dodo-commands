from fnmatch import fnmatch
import os

from dodo_commands.framework.config_io import ConfigIO


def get_layer_patterns(layer):
    return layer.get('ROOT', {}).get('layers', [])


class LayerCollector:
    def __init__(self, config_io=None):
        self.config_io = config_io or ConfigIO()
        self.layer_filenames = []

    def _skip(self, layer_filename):
        parts = os.path.basename(layer_filename).split('.')
        if len(parts) == 3:
            pattern = os.path.join(os.path.dirname(layer_filename),
                                   parts[0] + '.*.*')
            conflicts = [
                x for x in self.layer_filenames if fnmatch(x, pattern)
            ]
            for conflict in conflicts:
                if conflict != layer_filename:
                    raise Exception("Conflicting layers: %s and %s" %
                                    (conflict, layer_filename))
            if conflicts:
                return True
        return layer_filename in self.layer_filenames

    def glob(self, layer_patterns, recursive=False):
        new_layer_filenames = []
        for layer_filename in self.config_io.glob(layer_patterns):
            if not self._skip(layer_filename):
                self.layer_filenames.append(layer_filename)
                new_layer_filenames.append(layer_filename)

        if recursive:
            for layer_filename in new_layer_filenames:
                more_layer_patterns = self.load_layer_patterns(layer_filename)
                self.glob(more_layer_patterns, recursive)

    def load_layer_patterns(self, layer_filename):
        layer = self.config_io.load(layer_filename)
        return get_layer_patterns(layer)


def layer_filename_superset(layer_filenames=None,
                            recursive=True,
                            config_io=None):
    layer_collector = LayerCollector(config_io)
    layer_collector.glob(layer_filenames or ['config.yaml'], recursive)
    return layer_collector.layer_filenames
