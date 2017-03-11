# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.dodo_install_commands import DefaultsInstaller


class Command(DodoCommand):  # noqa
    help = (
        "Install default command directories supplied by the " +
        "paths argument."
    )
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            "paths",
            nargs='+',
            help='Create symlinks to these command directories'
        )

    def handle_imp(self, paths, **kwargs):  # noqa
        DefaultsInstaller().run(paths)
