import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import six
from dodo_commands.framework import ramda as R
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.config_key import Key
from dodo_commands.framework.global_config import load_global_config_parser
from dodo_commands.framework.paths import Paths

configparser = six.moves.configparser


def _args():
    parser = ArgumentParser(description=("Edit the dodo configuration files"))

    parser.add_argument(
        "--key", help="Only edit this key. Used in conjunction with --val"
    )
    parser.add_argument(
        "--val", help="The value to be used in conjunction with the --key option"
    )

    args = Dodo.parse_args(parser)

    if args.key or args.val:
        if not args.key and args.val:
            raise CommandError(
                "The options --key and --val should always be used together"
            )

    args.editor = load_global_config_parser().get("settings", "config_editor")
    args.config_dir = Dodo.get("/ROOT/config_dir")
    return args


if Dodo.is_main(__name__, safe=("--key" not in sys.argv)):
    try:
        args = _args()
    except configparser.NoOptionError as e:
        raise CommandError(
            "{error}. Please check {filename}".format(
                error=str(e), filename=Paths().global_config_filename()
            )
        )

    config = ConfigIO().load()

    if args.key and args.val:
        key = Key(config, args.key)
        key.set(args.val)
        ConfigIO().save(config)
        sys.exit(0)

    def add_global_config_filename(layer_paths):
        return R.concat(layer_paths, [Paths().global_config_filename()])

    x = Dodo.get_container().layers.get_ordered_layer_paths()
    x = add_global_config_filename(x)
    yaml_filenames = x

    Dodo.run(args.editor.split() + yaml_filenames, cwd=".")
