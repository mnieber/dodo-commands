from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.dodo_activate import Activator


def _args():
    parser = ArgumentParser()
    parser.add_argument('project', nargs='?')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--latest', action="store_true")
    group.add_argument('--create', action="store_true")
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=False):
    args = _args()
    if not args.project and not args.latest:
        raise CommandError("No project was specified")
    Activator().run(args.project, args.latest, args.create)
