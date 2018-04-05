from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from six.moves import configparser
import os


def _args():
    parser = ArgumentParser(
        description="Write a value of the global Dodo Command configuration"
    )
    parser.add_argument('key')
    parser.add_argument('val', nargs='?')
    args = Dodo.parse_args(parser)
    return args


def _config_filename():
    return os.path.expanduser("~/.dodo_commands/config")


def _write_config(config):
    """Save configuration."""
    with open(_config_filename(), "w") as f:
        config.write(f)


def _read_config():
    """Save configuration."""
    config = configparser.ConfigParser()
    config.read(_config_filename())
    return config


if Dodo.is_main(__name__, safe=False):
    args = _args()
    config = _read_config()
    section, key = args.key.split('.')
    if args.val:
        config.set(section, key, args.val)
        _write_config(config)
    else:
        print(config.get(section, key))
