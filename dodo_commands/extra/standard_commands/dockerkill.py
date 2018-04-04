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
    for line in docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}").split('\n'):
        if line:
            cid, name, image = line.split()
            result.append(dict(name=name, cid=cid, image=image))
    return result


if Dodo.is_main(__name__):
    args = _args()
    while True:
        containers = _containers()

        print("0 - exit")
        for idx, container in enumerate(containers):
            print("%d - %s" % (idx + 1, container['name']))
        print("999 - all of the above")

        print("\nSelect a container: ")
        raw_choice = int(raw_input())
        kill_all = raw_choice == 999
        choice = raw_choice - 1

        if choice == -1:
            sys.exit(0)
        elif kill_all:
            pass
        else:
            containers = [containers[choice]]
        for container in containers:
            Dodo.runcmd(
                ['docker', 'kill', container['cid']],
            )
        if kill_all:
            sys.exit(0)
