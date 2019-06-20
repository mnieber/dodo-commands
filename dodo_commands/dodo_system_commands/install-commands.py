from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import Paths
from dodo_commands.framework.util import is_using_system_dodo, symlink
from dodo_commands.framework.config import load_global_config_parser
import sys
import os
import tempfile


def _args():
    parser = ArgumentParser(
        description=("Install command packages into the global " +
                     "commands directory. " + _packages_in_extra_dir()))
    parser.add_argument("paths",
                        nargs='*',
                        help='Create symlinks to these command directories')
    parser.add_argument("--pip",
                        nargs='*',
                        help='Pip install the commands in these packages')
    parser.add_argument("--git",
                        nargs='*',
                        help='Clone a git repo into the commands directory')
    parser.add_argument("--remove",
                        action='store_true',
                        help='Remove commands from the commands directory')
    parser.add_argument("--to-defaults",
                        action='store_true',
                        help='Install into the default commands directory')

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--make-default",
        help=
        'Create a symlink to a global commands package in the default commands directory'
    )
    group.add_argument(
        "--remove-default",
        help=
        'Remove a symlink to a global commands package from the default commands directory'
    )
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


def _remove_package(package, only_from_defaults=False):
    """Install the dir with the default commands."""
    if not only_from_defaults:
        dest_dir = os.path.join(Paths().global_commands_dir(), package)
        if not os.path.exists(dest_dir):
            raise CommandError("Not installed: %s" % dest_dir)
        Dodo.run(['rm', '-rf', dest_dir])

    defaults_dest_dir = os.path.join(Paths().default_commands_dir(), package)
    if os.path.exists(defaults_dest_dir):
        Dodo.run(['rm', defaults_dest_dir])


def _install_package(package, install_commands_function, add_to_defaults):
    """Install the dir with the global commands."""
    dest_dir = os.path.join(Paths().global_commands_dir(), package)
    defaults_dest_dir = os.path.join(Paths().default_commands_dir(), package)

    if add_to_defaults and os.path.exists(defaults_dest_dir):
        _report_error("Error: already installed: %s" % defaults_dest_dir)
        return False

    if not install_commands_function():
        return False

    if add_to_defaults:
        if not os.path.exists(dest_dir):
            _report_error("Error: not found: %s" % dest_dir)
            return False

        if os.name == 'nt' and not args.confirm:
            symlink(dest_dir, defaults_dest_dir)
        else:
            Dodo.run(['ln', '-s', dest_dir, defaults_dest_dir])

    return True


def _install_commands_from_path(path, mv=False):
    """Install the dir with the global commands."""
    dest_dir = os.path.join(Paths().global_commands_dir(),
                            os.path.basename(path))

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
        Dodo.run(['mv', path, dest_dir])
    else:
        try:
            if os.name == 'nt' and not args.confirm:
                symlink(os.path.abspath(path), dest_dir)
            else:
                Dodo.run(['ln', '-s', os.path.abspath(path), dest_dir])
        except:
            _report_error("Error: could not create a symlink in %s." %
                          dest_dir)

    return True


def _install_commands_from_package(package):
    config = load_global_config_parser()
    python_path_parts = os.path.split(
        config.get("settings", "python_interpreter"))
    pip_path_parts = list(python_path_parts[:-1]) + [
        python_path_parts[-1].replace('python', 'pip')
    ]
    pip = os.path.join(*pip_path_parts)
    if not os.path.exists(pip):
        pip = os.path.splitext(pip)[0]
    Dodo.run([
        pip, 'install', '--upgrade', '--target',
        Paths().global_commands_dir(), package
    ])

    return True


def _clone_git_repo(repo_path):
    tmp_dir = tempfile.mkdtemp()
    Dodo.run(['git', 'clone', repo_path], cwd=tmp_dir)
    package = os.listdir(tmp_dir)[0]
    return tmp_dir, package


if Dodo.is_main(__name__):
    args = _args()
    if args.pip and not is_using_system_dodo():
        raise CommandError(
            "Please deactivate your dodo project first by running 'deactivate'."
        )

    if args.make_default:
        _install_package(args.make_default, lambda: True, True)
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
                    package, lambda: _install_commands_from_path(path),
                    args.to_defaults)

    if args.pip:
        for package in args.pip:
            if args.remove:
                _remove_package(package)
            else:
                _install_package(
                    package, lambda: _install_commands_from_package(package),
                    args.to_defaults)

    if args.git:
        for repo_path in args.git:
            if args.remove:
                raise CommandError(
                    "The --git option is not supported when removing a package."
                    + " Please use dodo install-commands --remove <package>.")

            tmp_dir, package = _clone_git_repo(repo_path)
            _install_package(
                package, lambda: _install_commands_from_path(
                    os.path.join(tmp_dir, package), mv=True), args.to_defaults)
            Dodo.run(['rm', '-rf', tmp_dir])
