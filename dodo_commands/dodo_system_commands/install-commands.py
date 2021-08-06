import os
import sys
import tempfile

from dodo_commands import CommandError, Dodo
from dodo_commands.framework.global_config import load_global_config_parser
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import (bordered, is_using_system_dodo,
                                          symlink)


def _args():
    parser = Dodo.parser

    parser.description = (
        "Install command packages into the global "
        + "commands directory. "
        + _packages_in_extra_dir()
    )
    parser.add_argument(
        "paths", nargs="*", help="Create symlinks to these command directories"
    )
    parser.add_argument(
        "--as",
        dest="as_directory",
        help="Use this name for the target commands directory",
    )
    parser.add_argument(
        "--pip", nargs="*", help="Pip install the commands in these packages"
    )
    parser.add_argument(
        "--git", nargs="*", help="Clone a git repo into the commands directory"
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove commands from the commands directory",
    )
    parser.add_argument(
        "--to-defaults",
        action="store_true",
        help="Install into the default commands directory",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--make-default",
        help="Create a symlink to a global commands package in the default commands directory",
    )
    group.add_argument(
        "--remove-default",
        help="Remove a symlink to a global commands package from the default commands directory",
    )

    return Dodo.parse_args()


def check_setuptools():
    if not Dodo.run([_python_path(), "-c", "import setuptools"]):
        _report_error(
            "\n"
            + bordered(
                "Error: your python version does not have setuptools installed.\n"
                + "Check the settings.python option in %s"
                % Paths().global_config_filename()
            )
        )
        sys.exit(1)


def _packages_in_extra_dir():
    extra_dir = Paths().extra_dir()
    packages = [
        x
        for x in os.listdir(extra_dir)
        if os.path.isdir(os.path.join(extra_dir, x)) and not x.startswith("__")
    ]

    if len(packages) == 0:
        return ""

    if len(packages) == 1:
        msg = " The %s package is found automagically " % packages[0]
    else:
        packages[-1] = "and " + packages[-1]
        msg = " The %s packages are found automagically " % ", ".join(packages)

    return (
        msg
        + " in the dodo_commands.extra package"
        + ", e.g. the following works: dodo install-commands %s." % packages[0]
    )


def _report_error(msg):
    sys.stderr.write(msg + os.linesep)


def _remove_package(package, only_from_defaults=False):
    """Install the dir with the default commands."""
    if not only_from_defaults:
        dest_dir = os.path.join(Paths().global_commands_dir(), package)
        if not os.path.exists(dest_dir):
            raise CommandError("Not installed: %s" % dest_dir)
        Dodo.run(["rm", "-rf", dest_dir])

    defaults_dest_dir = os.path.join(Paths().default_commands_dir(), package)
    if os.path.exists(defaults_dest_dir):
        Dodo.run(["rm", defaults_dest_dir])


def _install_package(package, as_directory, install_commands_function, add_to_defaults):
    """Install the dir with the global commands."""
    package_dirname = as_directory or package.replace('-', '_')
    dest_dir = os.path.join(Paths().global_commands_dir(), package_dirname)
    defaults_dest_dir = os.path.join(Paths().default_commands_dir(), package_dirname)

    if add_to_defaults and os.path.exists(defaults_dest_dir):
        _report_error("Error: already installed: %s" % defaults_dest_dir)
        return False

    if not install_commands_function(dest_dir):
        return False

    if add_to_defaults:
        if not os.path.exists(dest_dir):
            _report_error("Error: not found: %s" % dest_dir)
            return False

        Dodo.run(["ln", "-s", dest_dir, defaults_dest_dir])

    return True


def _install_commands_from_path(path, dest_dir, mv=False):
    """Install the dir with the global commands."""
    if not os.path.exists(path):
        alt_path = os.path.join(Paths().extra_dir(), path)
        if os.path.exists(alt_path):
            path = alt_path
        else:
            _report_error("Error: path not found: %s" % path)
            return False

    if os.path.exists(dest_dir):
        _report_error("Error: already installed: %s" % dest_dir)
        return False

    if mv:
        Dodo.run(["mv", path, dest_dir])
    else:
        try:
            Dodo.run(["ln", "-s", os.path.abspath(path), dest_dir])
        except Exception:
            _report_error("Error: could not create a symlink in %s." % dest_dir)

    return True


def _python_path():
    config = load_global_config_parser()
    return config.get("settings", "python_interpreter")


def _install_commands_from_package(package):
    Dodo.run(
        [
            _python_path(),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            Paths().global_commands_dir(),
            package,
        ]
    )

    return True


def _clone_git_repo(repo_path):
    tmp_dir = tempfile.mkdtemp()
    Dodo.run(["git", "clone", repo_path], cwd=tmp_dir)
    package = os.listdir(tmp_dir)[0]
    return tmp_dir, package


if Dodo.is_main(__name__):
    args = _args()
    if args.pip and not is_using_system_dodo():
        raise CommandError(
            "Please activate the default environment first by running 'dodo env default'."
        )

    if args.make_default:
        _install_package(args.make_default, None, lambda: True, True)
        sys.exit(0)

    if args.remove_default:
        _remove_package(args.remove_default, only_from_defaults=True)
        sys.exit(0)

    if args.paths:
        for path in args.paths:
            package = os.path.basename(path)
            if args.remove:
                _remove_package(package)
            else:
                _install_package(
                    package,
                    args.as_directory,
                    lambda dest_dir: _install_commands_from_path(path, dest_dir),
                    args.to_defaults,
                )

    if args.pip:
        check_setuptools()
        for package in args.pip:
            if args.remove:
                _remove_package(package)
            else:
                if args.as_directory:
                    raise CommandError(
                        "Sorry, the --as option is not supported when --pip is used."
                    )
                _install_package(
                    package,
                    args.as_directory,
                    lambda dest_dir: _install_commands_from_package(package),
                    args.to_defaults,
                )

    if args.git:
        for repo_path in args.git:
            if args.remove:
                raise CommandError(
                    "The --git option is not supported when removing a package."
                    + " Please use dodo install-commands --remove <package>."
                )

            tmp_dir, package = _clone_git_repo(repo_path)
            _install_package(
                package,
                args.as_directory,
                lambda dest_dir: _install_commands_from_path(
                    os.path.join(tmp_dir, package), dest_dir, mv=True
                ),
                args.to_defaults,
            )
            Dodo.run(["rm", "-rf", tmp_dir])
