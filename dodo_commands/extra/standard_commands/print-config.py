"""Print the full configuration."""

import yaml
from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--key')

    def handle_imp(self, key, **kwargs):  # noqa
        if key:
            print("%s" % str(self.get_config(key, '')))
        else:
            print(yaml.dump(self.config, default_flow_style=False, indent=4))
