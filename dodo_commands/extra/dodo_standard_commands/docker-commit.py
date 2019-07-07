from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from plumbum.cmd import docker
from six.moves import input as raw_input
import sys


def _args():
    parser = ArgumentParser()
    parser.add_argument('--by-container-name', dest='container_name')
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

    if args.container_name:
        filtered_containers = [
            x for x in containers if x.get('name') == args.container_name
        ]
        if not filtered_containers:
            raise CommandError("Container not found: %s" % args.container_name)
        assert len(filtered_containers) == 1
        container = filtered_containers[0]
    else:
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
