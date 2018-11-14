from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from plumbum.cmd import docker
from six.moves import input as raw_input
import sys


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


def _containers():
    result = []
    for line in docker("ps", "--format",
                       "{{.ID}} {{.Names}} {{.Image}}").split('\n'):
        if line:
            cid, name, image = line.split()
            result.append(dict(name=name, cid=cid, image=image))
    return result


if Dodo.is_main(__name__):
    args = _args()
    containers = _containers()

    print("0 - exit")
    for idx, container in enumerate(containers):
        print("%d - %s" % (idx + 1, container['name']))

    print("\nSelect a container: ")
    choice = int(raw_input()) - 1

    if choice == -1:
        sys.exit(0)

    container = containers[choice]

    Dodo.run([
        'docker',
        'commit',
        container['cid'],
        container['image'],
    ], )
