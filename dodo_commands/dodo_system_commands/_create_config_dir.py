import os

from dodo_commands.dependencies import (yaml_round_trip_dump,
                                        yaml_round_trip_load)
from dodo_commands.framework.config import merge_into_config
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

    default_config_mixin_filename = Paths().default_config_mixin_filename()
    if os.path.exists(default_config_mixin_filename):
        with open(default_config_mixin_filename) as f:
            default_config_mixin = yaml_round_trip_load(f.read())
            merge_into_config(default_config, default_config_mixin)

    with open(config_filename, "w") as f:
        for key in default_config:
            f.write(yaml_round_trip_dump({key: default_config[key]}))
            f.write(os.linesep)

    os.makedirs(os.path.join(config_dir, ".dodo-start-env"))
