"""Finds a directory or file inside the current project."""
from . import DodoCommand
from dodo_commands.framework.config import CommandPath
import os
import sys

script_src = """# noqa
from dodo_commands.system_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('foo')
        parser.add_argument(
            '--bar',
            required=True,
            help=''
        )

    def handle_imp(self, foo, bar, **kwargs):  # noqa
        self.runcmd(["echo"], cwd=".")
"""

class Command(DodoCommand):  # noqa
    help = "Creates a new Dodo command."
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument('name')
        parser.add_argument(
            '--next-to',
            required=True,
            help='Create the new command at the location of this command'
        )

    def handle_imp(self, name, next_to, **kwargs):  # noqa
        dest_path = None
        command_path = CommandPath(self.config)
        for item in command_path.items:
            script_path = os.path.join(
                item.full_path, next_to + ".py"
            )
            if os.path.exists(script_path):
                dest_path = os.path.join(
                    item.full_path, name + ".py"
                )

        if not dest_path:
            sys.stderr.write("Script not found: %s\n" % next_to)
            return

        with open(dest_path, "w") as f:
            f.write(script_src)

        print(dest_path)
