# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from plumbum import local
import os
import sys


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def handle_imp(self, **kwargs):  # noqa
        pip = local[os.path.join(os.path.dirname(sys.executable), "pip")]
        pip("install", "--upgrade", "dodo_commands")
