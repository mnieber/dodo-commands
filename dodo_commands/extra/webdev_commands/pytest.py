# noqa
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    decorators = ["docker"]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            [
                self.get_config("/PYTEST/pytest"),
                "-k", "test_accessibility_password_reset_recover_page"
            ],
            cwd=self.get_config("/PYTEST/src_dir")
        )
