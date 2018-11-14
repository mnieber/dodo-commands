from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import CommandPath
import os


def _args():
    parser = ArgumentParser(description="Creates a new Dodo command.")
    parser.add_argument('name')
    parser.add_argument(
        '--next-to',
        required=True,
        help='Create the new command at the location of this command')
    args = Dodo.parse_args(parser)
    return args


script = """
from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run([], cwd='.')
"""

if Dodo.is_main(__name__, safe=False):
    args = _args()
    dest_path = None
    command_path = CommandPath(Dodo.config)
    for item in command_path.items:
        script_path = os.path.join(item, args.next_to + ".py")
        if os.path.exists(script_path):
            dest_path = os.path.join(item, args.name + ".py")

    if not dest_path:
        raise CommandError("Script not found: %s" % args.next_to)

    if os.path.exists(dest_path):
        raise CommandError("Destination already exists: %s" % dest_path)

    with open(dest_path, "w") as f:
        f.write(script)
    print(dest_path)
