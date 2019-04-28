import argparse
import os
import sys
from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.command_map import get_command_map, execute_script
from dodo_commands.framework.config import CommandPath


def _args():
    parser = ArgumentParser(description='Download a command script and run it')

    parser.add_argument('url')
    parser.add_argument('script_args', nargs=argparse.REMAINDER)

    args = Dodo.parse_args(parser)
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    tmp_dir = os.path.join(os.path.expanduser('~'), '.dodo_commands', 'tmp')
    package_dir = os.path.join(tmp_dir, 'exec_scripts')

    if '.commands.yaml' in args.url:
        last_slash = args.url.rfind('/')
        url = args.url[:last_slash]
        cmd_name = args.url[last_slash + 1:]
    else:
        url = args.url
        cmd_name = os.path.splitext(os.path.basename(url))[0]

    Dodo.run(['mkdir', '-p', package_dir])
    Dodo.run(['touch', os.path.join(package_dir, '__init__.py')])
    Dodo.run(
        ['wget', url, '-O',
         os.path.join(package_dir, os.path.basename(url))])

    command_map = get_command_map(CommandPath([package_dir], []))
    sys.argv = sys.argv[1:]
    execute_script(command_map, cmd_name)
