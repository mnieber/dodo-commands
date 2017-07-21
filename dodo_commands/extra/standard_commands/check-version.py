"""Compare configuration version to version in original project config file."""
from . import DodoCommand
from dodo_commands.framework import get_version
from dodo_commands.framework.util import bordered
import os
import sys
import ruamel.yaml
from semantic_version import Version


class Command(DodoCommand):  # noqa
    def _get_version(self, config_filename):
        with open(config_filename) as f:
            config = ruamel.yaml.round_trip_load(f.read())
        return config.get("ROOT", {}).get("required_dodo_commands_version", "")

    def handle_imp(self, **kwargs):  # noqa
        config_filename = os.path.join(
            self.get_config("/ROOT/project_dir", ""),
            "dodo_commands",
            "res",
            "config.yaml"
        )

        required_version = self._get_version(config_filename)
        if required_version:
            actual_version = get_version()
            if Version(actual_version) < Version(required_version):
                sys.stdout.write(bordered(
                    'The dodo_commands package needs to be upgraded (%s < %s). Tip: use "dodo upgrade"'
                    % (
                        actual_version,
                        required_version,
                    ),
                ))
                sys.stdout.write('\n')
