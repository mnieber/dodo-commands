from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import (load_global_config_parser,
                                            write_global_config_parser)


def _args():
    parser = ArgumentParser(
        description="Write a value of the global Dodo Command configuration")
    parser.add_argument('key')
    parser.add_argument('val', nargs='?')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=False):
    args = _args()
    config = load_global_config_parser()

    if args.key.count('.') != 1:
        raise CommandError('The key should have the format <section>.<value>')

    section, key = args.key.split('.')
    if args.val:
        config.set(section, key, args.val)
        write_global_config_parser(config)
    else:
        print(config.get(section, key))
