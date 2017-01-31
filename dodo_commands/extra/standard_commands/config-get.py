# noqa
from dodo_commands.extra.standard_commands import DodoCommand
import sys


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('key')

    def handle_imp(self, key, **kwargs):  # noqa
        sys.stdout.write("%s\n" % str(self.get_config(key, '')))
