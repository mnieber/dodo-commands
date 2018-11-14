from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    parser.add_argument('what')
    parser.add_argument('where')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(['grep', '-rnw', args.where, '-e', "'{}'".format(args.what)], )
