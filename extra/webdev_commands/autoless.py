# noqa
from dodo_commands.defaults.commands.standard_commands import DodoCommand
import os

class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']

    def handle_imp(self, **kwargs):  # noqa
        css_dir = os.path.join(
            self.get_config("/ROOT/donationpage_src_dir"),
            "wordpress-theme",
            "css"
        )
        self.runcmd(
            [
                "autoless",
                ".",
                css_dir
            ],
            cwd=self.get_config("/LESS/src_dir")
        )
