"""Run gitk."""
from dodo_commands.system_commands import DodoCommand


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
