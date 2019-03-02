from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import CommandPath, ConfigIO
import os
import sys


def _default_commands_basename():
    return 'dodo_%s_commands' % Dodo.get_config('/ROOT/project_name')


def _default_commands_dir():
    return os.path.normpath(os.path.join(
        Dodo.get_config('/ROOT/shared_config_dir'),
        '..',
        _default_commands_basename()
    ))


def _args():
    parser = ArgumentParser(description="Creates a new Dodo command.")
    parser.add_argument('name')
    parser.add_argument(
        '--create-commands-dir',
        action='store_true',
        help="Create a directory for storing commands in the shared_config_dir",
    )
    parser.add_argument(
        '--next-to',
        help='Create the new command at the location of this command')
    args = Dodo.parse_args(parser)

    if not args.create_commands_dir and not args.next_to:
        raise CommandError('Either --create_commands_dir or --next-to is required')

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
        dest_path = os.path.join(_default_commands_dir(), args.name + ".py")
        command_path = CommandPath(Dodo.get_config())

        if not os.path.exists(_default_commands_dir()):
            Dodo.run(['mkdir', '-p', _default_commands_dir()])

        init_py = os.path.join(_default_commands_dir(), '__init__.py')
        if not os.path.exists(init_py):
            Dodo.run(['touch', init_py])

        if not [
            x for x in command_path.items
            if os.path.normpath(x) == _default_commands_dir()
        ]:
            config = ConfigIO().load(load_layers=False)
            scd = config['ROOT']['shared_config_dir']
            config['ROOT']['command_path'].append(
                os.path.join(scd[:scd.rfind('/')], _default_commands_basename())
            )
            ConfigIO().save(config)

    if args.next_to:
        dest_path = None
        command_path = CommandPath(Dodo.get_config())
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
