# noqa
from dodo_commands.defaults.commands.standard_commands import DodoCommand

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            ["less-watch-compiler", ".", "css"],
            cwd=self.get_config("/LESS/src_dir")
        )
