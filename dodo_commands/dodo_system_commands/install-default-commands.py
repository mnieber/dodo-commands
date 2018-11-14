from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import is_using_system_dodo, symlink
import sys
import os


def _args():
    parser = ArgumentParser(
        description=("Install default command directories supplied by the " +
                     "paths argument: dodo install-default-commands " +
                     "/path/to/my/commands. " + _packages_in_extra_dir()))
    parser.add_argument(
        "paths",
        nargs='*',
        help='Create symlinks to these command directories')
    parser.add_argument(
        "--pip", nargs='*', help='Pip install the commands in these packages')
    parser.add_argument(
        "--remove",
        action='store_true',
        help='Remove commands from the default commands directory')
    args = Dodo.parse_args(parser)
    return args


def _packages_in_extra_dir():
    extra_dir = Paths().extra_dir()
    packages = [
        x for x in os.listdir(extra_dir)
        if os.path.isdir(os.path.join(extra_dir, x)) and not x.startswith('__')
    ]

    if len(packages) == 0:
        return ""

    if len(packages) == 1:
        msg = " The %s package is found automagically " % packages[0]
    else:
        packages[-1] = "and " + packages[-1]
        msg = " The %s packages are found automagically " % ", ".join(packages)

    return (msg + " in the dodo_commands.extra package" +
            ", e.g. the following works: dodo install-default-commands %s." %
            packages[0])


def _report_error(msg):
    sys.stderr.write(msg + os.linesep)


def _remove_commands(path):
    """Install the dir with the default commands."""
    dest_dir = os.path.join(Paths().default_commands_dir(),
                            os.path.basename(path))

    if not os.path.exists(dest_dir):
        raise CommandError("Directory does not exist: %s" % dest_dir)
    Dodo.run(['rm', '-rf', dest_dir])


def _install_commands(path):
    """Install the dir with the default commands."""
    dest_dir = os.path.join(Paths().default_commands_dir(),
                            os.path.basename(path))

    if not os.path.exists(path):
        alt_path = os.path.join(Paths().extra_dir(), path)
        if os.path.exists(alt_path):
            path = alt_path
        else:
            _report_error("Error: path not found: %s" % path)
            return False

    if os.path.exists(dest_dir):
        return False

    try:
        if os.name == 'nt' and not args.confirm:
            symlink(os.path.abspath(path), dest_dir)
        else:
            Dodo.run(['ln', '-s', os.path.abspath(path), dest_dir])
    except:
        _report_error("Error: could not create a symlink in %s." % dest_dir)
        return False

    return True


def _remove_package(package):
    """Install the dir with the default commands."""
    dest_dir = os.path.join(Paths().default_commands_dir(), package)

    if not os.path.exists(dest_dir):
        raise CommandError("Directory does not exist: %s" % dest_dir)
    Dodo.run(['rm', '-rf', dest_dir])


def _install_package(package):
    pip = Paths().pip()
    if pip.startswith('/usr/') and not os.path.exists(pip):
        alt_pip = pip.replace("/usr/", "/usr/local/")
        if os.path.exists(alt_pip):
            pip = alt_pip
        else:
            raise CommandError(
                "Expected to find a pip executable at location %s or %s." %
                (pip, alt_pip))

    Dodo.run([
        pip, 'install', '--upgrade', '--target',
        Paths().default_commands_dir(), package
    ])


if Dodo.is_main(__name__):
    args = _args()
    if args.pip and not is_using_system_dodo():
        raise CommandError(
            "Please deactivate your dodo project first by running 'deactivate'."
        )

    if args.paths:
        for path in args.paths:
            if args.remove:
                _remove_commands(path)
            else:
                _install_commands(path)

    if args.pip:
        for package in args.pip:
            if args.remove:
                _remove_package(package)
            else:
                _install_package(package)
