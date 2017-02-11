"""Print the command line to cd to a folder inside the project folder."""
from . import DodoCommand
import sys


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument(
            'to',
            nargs='?',
            help=(
                'cd to /ROOT/<to>_dir. For example: dodo cd src ' +
                'cds to the value of /ROOT/src_dir.')
        )

    def handle_imp(self, to, **kwargs):
        path = self.get_config("/ROOT/%s_dir" % (to or 'project'))
        sys.stdout.write("cd %s\n" % path)
