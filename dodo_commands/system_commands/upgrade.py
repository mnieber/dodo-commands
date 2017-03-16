# noqa
from dodo_commands.system_commands import DodoCommand, CommandError
import os
import sys


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def handle_imp(self, **kwargs):  # noqa
        import dodo_commands
        dodo_commands_path = dodo_commands.__path__[0]
        if os.path.realpath(dodo_commands_path) != dodo_commands_path:
            raise CommandError("Please deactivate your dodo project first.")
        pip = os.path.join(os.path.dirname(sys.executable), "pip")
        self.runcmd([pip, "install", "--upgrade", "dodo_commands"])
