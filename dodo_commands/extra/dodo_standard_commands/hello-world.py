from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():  # noqa
    parser = ArgumentParser(description=('Print hello world.'))
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(['echo', 'Hello world'])
