from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from plumbum.cmd import docker
from six.moves import input as raw_input
import sys


def _args():
    parser = ArgumentParser()
    parser.add_argument('name', nargs='?')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    if not args.name:
        containers = [
            x for x in docker("ps", "--format", "{{.Names}}").split('\n') if x
        ]
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
        args.name,
        '/bin/bash',
    ], )
