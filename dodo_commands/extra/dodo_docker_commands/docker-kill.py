from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.choice_picker import ChoicePicker

docker = plumbum.cmd.docker


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


def _containers():
    result = []
    for line in docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}").split("\n"):
        if line:
            cid, name, image = line.split()
            result.append(dict(name=name, cid=cid, image=image))
    return result


if Dodo.is_main(__name__):
    args = _args()

    class Picker(ChoicePicker):
        def print_choices(self, choices):
            for idx, container in enumerate(choices):
                print("%d - %s" % (idx + 1, container["name"]))

        def question(self):
            return "Select a container: "

    picker = Picker(_containers())
    picker.pick()

    for container in picker.get_choices():
        Dodo.run(
            ["docker", "kill", container["cid"]],
        )
