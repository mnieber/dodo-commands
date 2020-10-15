import os

from dodo_commands.dependencies import yaml_round_trip_dump
from dodo_commands.framework.paths import Paths


def create_config_dir(config_dir):
    """Install the dir with dodo_commands resources."""
    os.makedirs(config_dir)
    config_filename = os.path.join(config_dir, "config.yaml")
    default_config = {
        "ROOT": {
            "command_path": [
                os.path.join(Paths().default_commands_dir(expanduser=False), "*")
            ],
            "version": "1.0.0",
        }
    }
    with open(config_filename, "w") as f:
        f.write(yaml_round_trip_dump(default_config))

    os.makedirs(os.path.join(config_dir, ".dodo-start-env"))
