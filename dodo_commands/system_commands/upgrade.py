# noqa
from dodo_commands.extra.standard_commands import DodoCommand
import os
import sys


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def handle_imp(self, **kwargs):  # noqa
        pip = os.path.join(os.path.dirname(sys.executable), "pip")
        self.runcmd([pip, "install", "--upgrade", "dodo_commands"])
