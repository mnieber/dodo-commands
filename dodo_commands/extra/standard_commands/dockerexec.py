# noqa
from dodo_commands.system_commands import DodoCommand
from plumbum.cmd import docker
from six.moves import input as raw_input


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('name', nargs='?')

    def handle_imp(self, name, **kwargs):  # noqa
        if not name:
            containers = [
                x for x in
                docker("ps", "--format", "{{.Names}}").split('\n')
                if x
            ]
            print("0 - exit")
            for idx, container in enumerate(containers):
                print("%d - %s" % (idx + 1, container))

            print("\nSelect a container: ")
            choice = int(raw_input()) - 1

            if choice == -1:
                return
            name = containers[choice]

        self.runcmd(
            [
                'docker',
                'exec',
                '-i',
                '-t',
                name,
                '/bin/bash',
            ],
        )
