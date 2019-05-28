from argparse import ArgumentParser
from configparser import NoOptionError
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import load_global_config_parser
import sys


def _args():
    parser = ArgumentParser(description='Print the command line to cd to'
                            ' a folder inside the project folder.')
    parser.add_argument(
        '--browse', action='store_true', help='Open file browser')

    parser.add_argument(
        'to',
        nargs='?',
        help=('cd to /ROOT/<to>_dir. For example: dodo cd src ' +
              'cds to the value of /ROOT/src_dir.'))
    args = Dodo.parse_args(parser)
    args.path = Dodo.get_config("/ROOT/%s_dir" % (args.to or 'project'))
    return args


if Dodo.is_main(__name__):
    args = _args()

    if args.browse:
        try:
            browser = load_global_config_parser().get("settings",
                                                      "file_browser")
        except NoOptionError:
            raise CommandError(
                "The file_browser option was not found in the global configuration."
            )
        Dodo.run([browser, args.path])

    sys.stdout.write("cd %s\n" % args.path)
