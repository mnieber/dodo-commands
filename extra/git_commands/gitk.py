"""Run gitk."""
from dodo_commands.default_commands.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    def handle_imp(  # noqa
        self, **kwargs
    ):
        self.runcmd(
            [
                "gitk",
            ],
            cwd=self.get_config("/ROOT/src_dir"),
        )
