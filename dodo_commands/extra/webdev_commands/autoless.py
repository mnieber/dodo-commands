# noqa
from dodo_commands.default_commands.standard_commands import DodoCommand

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            [
                "autoless",
                ".",
                self.get_config("/LESS/output_dir")
            ],
            cwd=self.get_config("/LESS/src_dir")
        )
