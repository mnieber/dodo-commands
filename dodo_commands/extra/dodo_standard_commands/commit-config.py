from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.config import Paths
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        '--message', '-m', dest='message', help='The commit message')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if not os.path.exists(os.path.join(Paths().res_dir(), '.git')):
        Dodo.run(['git', 'init'], cwd=Paths().res_dir())

    Dodo.run(['git', 'add', '-A'], cwd=Paths().res_dir())
    Dodo.run(['git', 'commit', '-m', args.message or 'Update configuration'],
             cwd=Paths().res_dir())
