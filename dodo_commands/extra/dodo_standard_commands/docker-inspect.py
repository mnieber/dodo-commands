from argparse import ArgumentParser
import sys

from plumbum.cmd import docker
from dodo_commands.framework.choice_picker import ChoicePicker

from dodo_commands import Dodo


def _args():
    parser = ArgumentParser()
    parser.add_argument('--find')
    parser.add_argument('--ip', action='store_true')
    args = Dodo.parse_args(parser)
    args.name = None
    return args


def _containers():
    return [x for x in docker("ps", "--format", "{{.Names}}").split('\n') if x]


if Dodo.is_main(__name__):
    args = _args()

    if args.find:
        for container in _containers():
            if args.find in container:
                args.name = container
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
        args.name = picker.get_choices()[0]

    ip_args = ["-f", "{{ .NetworkSettings.IPAddress }}"] if args.ip else []
    Dodo.run(['docker', 'inspect', *ip_args, args.name], )
