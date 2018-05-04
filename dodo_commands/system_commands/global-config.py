from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.config import (
    get_global_config, global_config_filename
)


def _args():
    parser = ArgumentParser(
        description="Write a value of the global Dodo Command configuration"
    )
    parser.add_argument('key')
    parser.add_argument('val', nargs='?')
    args = Dodo.parse_args(parser)
    return args


def _write_config(config):
    """Save configuration."""
    with open(global_config_filename(), "w") as f:
        config.write(f)


if Dodo.is_main(__name__, safe=False):
    args = _args()
    config = get_global_config()
    section, key = args.key.split('.')
    if args.val:
        config.set(section, key, args.val)
        _write_config(config)
    else:
        print(config.get(section, key))
