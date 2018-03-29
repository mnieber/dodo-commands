# noqa
from dodo_commands.system_commands import DodoCommand
from plumbum.cmd import docker
from six.moves import input as raw_input


class Command(DodoCommand):  # noqa
    help = ""

    def _containers(self):
        result = []
        for line in docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}").split('\n'):
            if line:
                cid, name, image = line.split()
                result.append(dict(name=name, cid=cid, image=image))
        return result

    def handle_imp(self, **kwargs):  # noqa
        while True:
            containers = self._containers()

            print("0 - exit")
            for idx, container in enumerate(containers):
                print("%d - %s" % (idx + 1, container['name']))
            print("999 - all of the above")

            print("\nSelect a container: ")
            raw_choice = int(raw_input())
            kill_all = raw_choice == 999
            choice = raw_choice - 1

            if choice == -1:
                return
            elif kill_all:
                pass
            else:
                containers = [containers[choice]]
            for container in containers:
                self.runcmd(
                    ['docker', 'kill', container['cid']],
                )
            if kill_all:
                return
