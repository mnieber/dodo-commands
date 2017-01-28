"""Script for activating/creating a project in the projects dir."""
import argparse
import os
import sys


class DefaultsInstaller:
    """Adds subdirectories to default_commands."""

    def _args(self):
        """Get command line args."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "paths",
            nargs='+',
            help='Create symlinks to these command directories'
        )

        return parser.parse_args()

    def _report_error(self, msg):
        sys.stderr.write(msg + os.linesep)

    def _install_commands(self, path):
        """Install the dir with the default commands."""
        dest_dir = os.path.join(
            os.path.expanduser("~/.dodo_commands/default_commands"),
            os.path.basename(path)
        )

        if not os.path.exists(path):
            import dodo_commands
            extra_dir = os.path.join(
                os.path.dirname(dodo_commands.__file__), "extra"
            )
            alt_path = os.path.join(extra_dir, path)
            if os.path.exists(alt_path):
                path = alt_path
            else:
                self._report_error("Error: path not found: %s" % path)
                return False

        if os.path.exists(dest_dir):
            self._report_error("%s already exists (no changes were made)." % dest_dir)
            return False

        try:
            os.symlink(os.path.abspath(path), dest_dir)
        except:
            self._report_error("Error: could not create a symlink in %s." % dest_dir)
            return False

        return True

    def run(self):
        """Activate or create a project in the projects dir."""
        for path in self._args().paths:
            self._install_commands(path)


def main():  # noqa
    DefaultsInstaller().run()
