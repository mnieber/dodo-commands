import os
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import six
from dodo_commands.framework.command_map import get_command_map
from dodo_commands.framework.command_path import get_command_dirs_from_config

raw_input = six.moves.input


def _args():
    parser = ArgumentParser(description="Creates a new Dodo command.")
    parser.add_argument("name")
    parser.add_argument("--next-to")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing command script"
    )

    args = Dodo.parse_args(parser)
    return args


script_py = """from argparse import ArgumentParser

from dodo_commands import Dodo, ConfigArg, CommandError


def _args():
    # Create the parser
    parser = ArgumentParser(description='')
    parser.add_argument('foo')

    # Use the parser to create the command arguments
    args = Dodo.parse_args(parser, config_args=[])
    args.cwd = Dodo.get('/ROOT/project_dir')

    # Raise an error if something is not right
    if False:
        raise CommandError('Oops')

    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(['echo', args.foo], cwd=args.cwd)
"""


def handle_next_to(args):
    command_dirs = get_command_dirs_from_config(Dodo.get())
    command_map = get_command_map(command_dirs)

    if args.next_to:
        item = command_map.get(args.next_to)
        if not item:
            raise CommandError("Script not found: %s" % args.next_to)
        dest_path = os.path.join(os.path.dirname(item.filename), args.name + ".py")

        if os.path.exists(dest_path) and not args.force:
            raise CommandError("Destination already exists: %s" % dest_path)

        with open(dest_path, "w") as f:
            f.write(
                script_py.format(
                    parser_args_str="", params_str="", description="", args_str=""
                )
            )
        print(dest_path)
    else:
        print(
            script_py.format(
                parser_args_str="", params_str="", description="", args_str=""
            )
        )


if Dodo.is_main(__name__, safe=False):
    args = _args()
    handle_next_to(args)
