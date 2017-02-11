# noqa
from dodo_commands.extra.standard_commands import DodoCommand

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']

    def handle_imp(self, **kwargs):  # noqa
        autoless = self.get_config("/LESS/autoless", "autoless")
        self.runcmd(
            [
                "mkdir",
                "-p",
                self.get_config("/LESS/output_dir")
            ]
        )

        self.runcmd(
            [
                autoless,
                ".",
                self.get_config("/LESS/output_dir")
            ],
            cwd=self.get_config("/LESS/src_dir")
        )
