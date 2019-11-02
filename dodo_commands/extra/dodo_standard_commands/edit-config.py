from argparse import ArgumentParser
import sys
from six.moves import configparser

from funcy.py2 import concat

from dodo_commands import Dodo, CommandError
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.global_config import load_global_config_parser
from dodo_commands.framework.config_expander import Key
from dodo_commands.framework.container.utils import get_ordered_layer_paths


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

    config = ConfigIO().load()

    if args.key and args.val:
        xpath = [x for x in args.key.split('/') if x]
        key = Key(config, xpath)
        key.set(args.val)
        ConfigIO().save(config)
        sys.exit(0)

    def add_global_config_filename(layer_paths):
        return concat(layer_paths, [Paths().global_config_filename()])

    x = get_ordered_layer_paths(Dodo.get_container())
    x = add_global_config_filename(x)
    yaml_filenames = x

    Dodo.run(args.editor.split() + yaml_filenames, cwd='.')
