"""Run the webpack command."""
from dodo_commands.defaults.commands.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    decorators = ['docker']

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            ["webpack", "--watch-stdin"],
            cwd=self.get_config("/WEBPACK/webpack_dir")
        )
