from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import (load_global_config_parser,
                                            ConfigIO, Paths, ConfigLoader)
from dodo_commands.framework.config_expander import Key
from six.moves import configparser
import os
import sys


def _args():
    parser = ArgumentParser(description=('Edit the dodo configuration files'))

    parser.add_argument(
        '--key', help='Only edit this key. Used in conjunction with --val')
    parser.add_argument(
        '--val',
        help='The value to be used in conjunction with the --key option')

    args = Dodo.parse_args(parser)

    if args.key or args.val:
        if not args.key and args.val:
            raise CommandError(
                "The options --key and --val should always be used together")

    args.editor = load_global_config_parser().get("settings", "config_editor")
    args.res_dir = Dodo.get_config('/ROOT/res_dir')
    return args


if Dodo.is_main(__name__, safe=('--key' not in sys.argv)):
    try:
        args = _args()
    except configparser.NoOptionError as e:
        raise CommandError("{error}. Please check {filename}".format(
            error=str(e), filename=Paths().global_config_filename()))

    if args.key and args.val:
        config = ConfigIO().load()
        xpath = [x for x in args.key.split('/') if x]
        key = Key(config, xpath)
        key.set(args.val)
        ConfigIO().save(config)
        sys.exit(0)

    yaml_filenames = ([os.path.join(args.res_dir, 'config.yaml')] +
                      ConfigLoader().get_layers(Dodo.get_config()))

    yaml_filenames.append(Paths().global_config_filename())
    Dodo.run(args.editor.split() + yaml_filenames, cwd='.')
