# noqa
from dodo_commands.system_commands import DodoCommand, CommandError
import sys
import os


def _extra_dir():
    import dodo_commands
    return os.path.join(
        os.path.dirname(dodo_commands.__file__), "extra"
    )


class Command(DodoCommand):  # noqa
    help = (
        "Install default command directories supplied by the " +
        "paths argument."
    )
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            "paths",
            nargs='*',
            help='Create a symlink to these command directories'
        )
        parser.add_argument(
            "--pip",
            nargs='*',
            help='Pip install the commands in these packages and create symlinks'
        )

    def _report_error(self, msg):
        sys.stderr.write(msg + os.linesep)

    def _install_commands(self, path):
        """Install the dir with the default commands."""
        dest_dir = os.path.join(
            os.path.expanduser("~/.dodo_commands/default_commands"),
            os.path.basename(path)
        )

        if not os.path.exists(path):
            alt_path = os.path.join(_extra_dir(), path)
            if os.path.exists(alt_path):
                path = alt_path
            else:
                self._report_error("Error: path not found: %s" % path)
                return False

        if os.path.exists(dest_dir):
            return False

        try:
            os.symlink(os.path.abspath(path), dest_dir)
        except:
            self._report_error("Error: could not create a symlink in %s." % dest_dir)
            return False

        return True

    def _install_package(self, package):
        pip = os.path.join(os.path.dirname(sys.executable), "pip")
        default_commands_dir = os.path.expanduser("~/.dodo_commands/default_commands")
        self.runcmd([
            pip, 'install', '--upgrade', '--target', default_commands_dir, package
        ])

    def handle_imp(self, paths, pip, **kwargs):  # noqa
        import dodo_commands
        dodo_commands_path = dodo_commands.__path__[0]
        if os.path.realpath(dodo_commands_path) != dodo_commands_path:
            raise CommandError("Please deactivate your dodo project first.")

        for path in paths:
            self._install_commands(path)

        for package in pip:
            self._install_package(package)
