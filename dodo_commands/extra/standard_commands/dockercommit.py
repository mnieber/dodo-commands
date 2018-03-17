# noqa
from dodo_commands.system_commands import DodoCommand
from plumbum.cmd import docker
from six.moves import input as raw_input


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('name', nargs='?')

    def _containers(self):
        result = []
        for line in docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}").split('\n'):
            if line:
                cid, name, image = line.split()
                result.append(dict(name=name, cid=cid, image=image))
        return result

    def handle_imp(self, name, **kwargs):  # noqa
        if not name:
            containers = self._containers()

            print("0 - exit")
            for idx, container in enumerate(containers):
                print("%d - %s" % (idx + 1, container['name']))

            print("\nSelect a container: ")
            choice = int(raw_input()) - 1

            if choice == -1:
                return
            container = containers[choice]

        self.runcmd(
            [
                'docker',
                'commit',
                container['cid'],
                container['image'],
            ],
        )
