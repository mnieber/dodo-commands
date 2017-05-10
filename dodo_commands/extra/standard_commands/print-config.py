"""Print the full configuration."""

import ruamel.yaml
import re
from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--key')

    def handle_imp(self, key, **kwargs):  # noqa
        if key:
            print("%s" % str(self.get_config(key, '')))
        else:
            content = re.sub(
                r'^([0-9_A-Z]+\:)$',
                r'\n\1',
                ruamel.yaml.round_trip_dump(self.config),
                flags=re.MULTILINE
            )
            print(
                re.sub(
                    r'^\n\n',
                    r'\n',
                    content,
                    flags=re.MULTILINE
                )
            )
