# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.dodo_activate import Activator


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('project', nargs='?')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--latest', action="store_true")
        group.add_argument('--create', action="store_true")

    def handle_imp(self, project, latest, create, **kwargs):  # noqa
        Activator().run(project, latest, create)
