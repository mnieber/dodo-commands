from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.config import expand_keys


def _args():
    parser = ArgumentParser()
    parser.add_argument('text')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    print(expand_keys(Dodo.get_config(), args.text))
