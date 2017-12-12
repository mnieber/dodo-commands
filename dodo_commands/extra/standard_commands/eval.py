# noqa
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.config import expand_keys


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'text'
        )

    def handle_imp(self, text, **kwargs):  # noqa
        print(expand_keys(text, self.config))
