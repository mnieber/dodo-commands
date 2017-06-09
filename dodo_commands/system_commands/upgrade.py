# noqa
from dodo_commands.system_commands import DodoCommand, CommandError
import os
import sys


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument(
            '--sudo',
            action='store_true',
        )

    def handle_imp(self, sudo, **kwargs):  # noqa
        import dodo_commands
        dodo_commands_path = dodo_commands.__path__[0]
        if os.path.realpath(dodo_commands_path) != dodo_commands_path:
            raise CommandError("Please deactivate your dodo project first by running 'deactivate'.")
        pip = os.path.join(os.path.dirname(sys.executable), "pip")

        if sudo:
            self.runcmd(["sudo", pip, "install", "--upgrade", "dodo_commands"])
        else:
            self.runcmd([pip, "install", "--upgrade", "dodo_commands"])
