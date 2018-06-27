from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import sys


def _args():
    parser = ArgumentParser(description='Print the command line to cd to'
                            ' a folder inside the project folder.')
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
    sys.stdout.write("cd %s\n" % args.path)
