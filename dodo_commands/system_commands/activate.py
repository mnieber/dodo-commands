# noqa
from dodo_commands.system_commands import DodoCommand, CommandError
from dodo_commands.dodo_activate import Activator


class Command(DodoCommand):  # noqa
    help = ""
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('project', nargs='?')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--latest', action="store_true")
        group.add_argument('--create', action="store_true")

    def handle_imp(self, project, latest, create, **kwargs):  # noqa
        if not project and not latest:
            raise CommandError("No project was specified")
        Activator().run(project, latest, create)
