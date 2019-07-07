from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser(description='Run docker compose')

    parser.add_argument('compose_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.cwd = Dodo.get_config('/ROOT/src_dir')
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(['docker-compose'] + remove_trailing_dashes(args.compose_args),
             cwd=args.cwd)
