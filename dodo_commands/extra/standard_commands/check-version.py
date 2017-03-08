"""Compare configuration version to version in original project config file."""
from . import DodoCommand
import os
import sys
import yaml


class Command(DodoCommand):  # noqa
    def _get_version(self, config_filename):
        with open(config_filename) as f:
            config = yaml.load(f.read())
        version = config.get("ROOT", {}).get("required_dodo_commands_version", "").split(".")
        return [x for x in version if x != ""]

    def handle_imp(self, **kwargs):  # noqa
        config_filename = os.path.join(
            self.get_config("/ROOT/project_dir", ""),
            "dodo_commands",
            "res",
            "config.yaml"
        )

        required_version = self._get_version(config_filename)
        if required_version:
            actual_version = DodoCommand.get_version().split(".")
            if required_version > actual_version:
                sys.stdout.write(
                    'The dodo_commands package needs to be upgraded (%s < %s). Tip: use "dodo-upgrade"\n'
                    % (
                        ".".join(actual_version),
                        ".".join(required_version),
                    ),
                )
