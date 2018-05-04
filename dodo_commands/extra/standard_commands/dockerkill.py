from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from plumbum.cmd import docker
from six.moves import input as raw_input
import re


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


def _filter_choices(all_choices, raw_choice):
    regexp = r"(\d)+(\-(\d)+)?,?"
    result = []
    span = [None, None]
    for choice in [x for x in re.finditer(regexp, raw_choice)]:
        if span[0] is None:
            span[0] = choice.span()[0]
        if span[1] is None or span[1] == choice.span()[0]:
            span[1] = choice.span()[1]
        from_index = int(choice.group(1)) - 1
        to_index = int(choice.group(3)) - 1 if choice.group(3) else from_index
        for idx in range(from_index, to_index + 1):
            result.append(all_choices[idx])
    return result, span


if Dodo.is_main(__name__):
    args = _args()
    containers = _containers()

    for idx, container in enumerate(containers):
        print("%d - %s" % (idx + 1, container['name']))

    raw_choice = raw_input("Select a container: ")

    selected_containers, span = _filter_choices(containers, raw_choice)
    if span == [0, len(raw_choice)]:
        for container in selected_containers:
            Dodo.runcmd(
                ['docker', 'kill', container['cid']],
            )
    else:
        raise CommandError("Syntax error")
