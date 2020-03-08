import sys
from argparse import ArgumentParser
from configparser import NoOptionError

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum, six
from dodo_commands.framework.global_config import load_global_config_parser

docker = plumbum.cmd.docker
raw_input = six.moves.input


def _args():
    parser = ArgumentParser()
    parser.add_argument('--user')
    parser.add_argument('--find')
    parser.add_argument('name', nargs='?')
    parser.add_argument('--cmd')
    args = Dodo.parse_args(parser)

    config = load_global_config_parser()

    try:
        default_shell = config.get("settings", "shell")
    except NoOptionError:
        default_shell = '/bin/bash'

    args.cmd = args.cmd or default_shell

    return args


def _containers():
    return [x for x in docker("ps", "--format", "{{.Names}}").split('\n') if x]


if Dodo.is_main(__name__):
    args = _args()

    if args.find:
        args.name = None
        for container in _containers():
            if args.find in container:
                args.name = container
                break
        if not args.name:
            raise CommandError("Container not found: %s" % args.find)
    elif not args.name:
        containers = _containers()
        print("0 - exit")
        for idx, container in enumerate(containers):
            print("%d - %s" % (idx + 1, container))

        print("\nSelect a container: ")
        choice = int(raw_input()) - 1

        if choice == -1:
            sys.exit(0)

        args.name = containers[choice]

    Dodo.run([
        'docker',
        'exec',
        '-i',
        '-t',
    ] + (['--user', args.user] if args.user else []) + [
        args.name,
        args.cmd,
    ], )
