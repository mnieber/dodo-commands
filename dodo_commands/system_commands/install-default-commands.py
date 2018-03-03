# noqa
from dodo_commands.system_commands import DodoCommand, CommandError
from dodo_commands.framework.util import is_using_system_dodo

import sys
import os


def _extra_dir():
    import dodo_commands
    return os.path.join(
        os.path.dirname(dodo_commands.__file__), "extra"
    )


def _packages_in_extra_dir():
    extra_dir = _extra_dir()
    packages = [
        x for x in os.listdir(extra_dir)
        if os.path.isdir(os.path.join(extra_dir, x))
        and not x.startswith('__')
    ]

    if len(packages) == 0:
        return ""

    if len(packages) == 1:
        msg = " The %s package is found automagically " % packages[0]
    else:
        packages[-1] = "and " + packages[-1]
        msg = " The %s packages are found automagically " % ", ".join(packages)

    return (
        msg + " in the dodo_commands.extra package" +
        ", e.g. the following works: dodo install-default-commands %s." % packages[0]
    )


class Command(DodoCommand):  # noqa
    help = (
        "Install default command directories supplied by the " +
        "paths argument: dodo install-default-commands " +
        "/path/to/my/commands. " + _packages_in_extra_dir()
    )
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            "paths",
            nargs='*',
            help='Create symlinks to these command directories'
        )
        parser.add_argument(
            "--pip",
            nargs='*',
            help='Pip install the commands in these packages'
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
        if pip.startswith('/usr/') and not os.path.exists(pip):
            alt_pip = pip.replace("/usr/", "/usr/local/")
            if os.path.exists(alt_pip):
                pip = alt_pip
            else:
                raise CommandError(
                    "Expected to find a pip executable at location %s or %s."
                    % (pip, alt_pip)
                )

        default_commands_dir = os.path.expanduser("~/.dodo_commands/default_commands")
        self.runcmd([
            pip, 'install', '--upgrade', '--target', default_commands_dir, package
        ])

    def handle_imp(self, paths, pip, **kwargs):  # noqa
        if pip and not is_using_system_dodo():
            raise CommandError("Please deactivate your dodo project first by running 'deactivate'.")

        if paths:
            for path in paths:
                self._install_commands(path)

        if pip:
            for package in pip:
                self._install_package(package)
