# noqa
from dodo_commands.system_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('what')
        parser.add_argument('where')

    def handle_imp(self, what, where, **kwargs):  # noqa
        self.runcmd(
            [
                'grep', '-rnw', where, '-e', what
            ],
        )
