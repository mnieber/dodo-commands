from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import get_command_path, ConfigIO
from dodo_commands.framework.command_map import get_command_map
import os
import sys


def _new_commands_dir():
    def _new_commands_basename():
        return 'dodo_%s_commands' % Dodo.get_config('/ROOT/project_name')

    return os.path.normpath(
        os.path.join(
            Dodo.get_config('/ROOT/shared_config_dir'), '..',
            _new_commands_basename()))


def _args():
    parser = ArgumentParser(description="Creates a new Dodo command.")
    parser.add_argument('name')
    parser.add_argument(
        '--create-commands-dir',
        nargs='?',
        const=True,
        help="Create a directory for storing commands in the shared_config_dir",
    )
    parser.add_argument(
        '--next-to',
        help='Create the new command at the location of this command')
    args = Dodo.parse_args(parser)

    if not args.create_commands_dir and not args.next_to:
        raise CommandError(
            'Either --create-commands-dir or --next-to is required')

    return args


script = """import os
from argparse import ArgumentParser
from dodo_commands.framework import Dodo, ConfigArg, CommandError


def _args():
    parser = ArgumentParser(
        description='A new command that runs in the project\\\'s "res" directory'
    )

    # Add arguments to the parser here
    parser.add_argument('name')

    # Parse the arguments.
    # Optionally, use `config_args` to include additional arguments whose values
    # come either from the configuration file or from the command line (see docs).
    args = Dodo.parse_args(parser, config_args=[
        ConfigArg('/ROOT/res_dir', '--cwd')
    ])

    # Insert additional arguments after parsing
    args.project_name = Dodo.get_config('/ROOT/project_name')

    # Raise an error if something is not right
    if not os.path.exists(args.cwd):
        raise CommandError('Not found: %s' % args.cwd)

    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(['echo', args.name, args.project_name], cwd=args.cwd)
"""

if Dodo.is_main(__name__, safe='--create-commands-dir' not in sys.argv):
    args = _args()

    if args.create_commands_dir:
        project_dir = Dodo.get_config('/ROOT/project_dir')
        new_commands_dir = (_new_commands_dir() if
                            args.create_commands_dir is True else os.path.join(
                                project_dir, args.create_commands_dir))
        dest_path = os.path.join(new_commands_dir, args.name + ".py")
        command_path = get_command_path(Dodo.get_config())

        if not os.path.exists(new_commands_dir):
            Dodo.run(['mkdir', '-p', new_commands_dir])

        init_py = os.path.join(new_commands_dir, '__init__.py')
        if not os.path.exists(init_py):
            Dodo.run(['touch', init_py])

        if not [
                x for x in command_path.items
                if os.path.normpath(x) == new_commands_dir
        ]:
            config = ConfigIO().load()
            config['ROOT']['command_path'].append(new_commands_dir)
            ConfigIO().save(config)

    if args.next_to:
        command_map = get_command_map()
        item = command_map.get(args.next_to)

        if not item:
            raise CommandError("Script not found: %s" % args.next_to)

        dest_path = os.path.join(
            os.path.dirname(item.filename), args.name + ".py")

    if os.path.exists(dest_path):
        raise CommandError("Destination already exists: %s" % dest_path)

    with open(dest_path, "w") as f:
        f.write(script)
    print(dest_path)
