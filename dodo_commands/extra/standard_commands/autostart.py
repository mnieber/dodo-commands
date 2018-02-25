# noqa
from dodo_commands.system_commands import DodoCommand
import os


class Command(DodoCommand):  # noqa
    help = (
        "Writes (or removes) a small script that activates the latest " +
        "Dodo Commands project"
    )
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('status', choices=['on', 'off'])

    def handle_imp(self, status, **kwargs):  # noqa
        script = os.path.expanduser("~/.dodo_commands_autostart")
        if status == "on" and not os.path.exists(script):
            with open(script, "w") as f:
                f.write("$(dodo activate --latest)\n")
                f.write("dodo check-version --dodo --config\n")
        if status == "off" and os.path.exists(script):
            os.unlink(script)
