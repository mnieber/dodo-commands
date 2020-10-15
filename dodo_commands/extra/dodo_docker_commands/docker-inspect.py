import sys
from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.choice_picker import ChoicePicker

docker = plumbum.cmd.docker


def _args():
    parser = ArgumentParser()
    parser.add_argument("--find")
    parser.add_argument("--ip", action="store_true")
    args = Dodo.parse_args(parser)
    args.names = []
    return args


def _containers():
    return [x for x in docker("ps", "--format", "{{.Names}}").split("\n") if x]


if Dodo.is_main(__name__):
    args = _args()

    if args.find:
        for container in _containers():
            if args.find in container:
                args.names = [container]
                break
    else:

        class Picker(ChoicePicker):
            def print_choices(self, choices):
                print("0 - exit")
                for idx, container in enumerate(choices):
                    print("%d - %s" % (idx + 1, container))
                print()

            def question(self):
                return "Select a container: "

            def on_invalid_index(self, index):
                if index == 0:
                    sys.exit(0)

        picker = Picker(_containers())
        picker.pick()
        args.names = picker.get_choices()

    ip_args = (
        ["-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"]
        if args.ip
        else []
    )
    for container in args.names:
        Dodo.run(
            ["docker", "inspect", *ip_args, container],
        )
