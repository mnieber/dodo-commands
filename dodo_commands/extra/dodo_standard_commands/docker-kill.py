from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.util import filter_choices
from plumbum.cmd import docker
from six.moves import input as raw_input


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

    for idx, container in enumerate(containers):
        print("%d - %s" % (idx + 1, container['name']))

    raw_choice = raw_input("Select a container: ")

    selected_containers, span = filter_choices(containers, raw_choice)
    if span == [0, len(raw_choice)]:
        for container in selected_containers:
            Dodo.run(['docker', 'kill', container['cid']], )
    else:
        raise CommandError("Syntax error")
