from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import CommandPath, load_global_config_parser
from dodo_commands.framework.util import chop
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument('package', choices=_package_to_drop_src_dir().keys())
    args = Dodo.parse_args(parser)
    return args


def _diff_tool():
    return load_global_config_parser().get("settings", "diff_tool")


def _read_dot_drop_path(path):
    with open(path) as ifs:
        base_dir = os.path.realpath(os.path.dirname(path))
        rel_dir = chop(ifs.read())
        return os.path.realpath(os.path.join(base_dir, rel_dir))


def _add_drop_src_dir(package_to_drop_src_dir, package_name, drop_src_dir):
    if package_name in package_to_drop_src_dir:
        if drop_src_dir == package_to_drop_src_dir[package_name]:
            return
        else:
            print('Warning: Found two drop directories for package %s:\n' %
                  package_name)
            print(drop_src_dir)
            print(package_to_drop_src_dir[package_name])
    package_to_drop_src_dir[package_name] = drop_src_dir


def _dot_drop_path(item):
    result = os.path.join(item, '.drop-in')
    return result if os.path.exists(result) else None


def _drop_src_dir(item):
    result = os.path.join(item, 'drop-in')
    return result if os.path.isdir(result) else None


def _package_to_drop_src_dir():
    package_to_drop_src_dir = {}
    command_path = CommandPath(Dodo.config)
    for item in command_path.items:
        dot_drop_path = _dot_drop_path(item)
        drop_src_dir = _drop_src_dir(item)

        if dot_drop_path and drop_src_dir:
            print(
                "Warning: found two drop-ins where only one was expected:\n%s\n%s"
                % (dot_drop_path, drop_src_dir))

        package_name = os.path.basename(item)
        if drop_src_dir:
            _add_drop_src_dir(package_to_drop_src_dir, package_name,
                              drop_src_dir)

        if dot_drop_path:
            _add_drop_src_dir(package_to_drop_src_dir, package_name,
                              _read_dot_drop_path(dot_drop_path))

    return package_to_drop_src_dir


if Dodo.is_main(__name__, safe=True):
    args = _args()

    drop_src_dir = _package_to_drop_src_dir().get(args.package)
    if not drop_src_dir:
        raise CommandError("No drop-in found for package %s" % args.package)

    if not os.path.isdir(drop_src_dir):
        raise CommandError(
            "The drop-in directory does not exist: %s" % drop_src_dir)

    res_dir = Dodo.get_config('/ROOT/res_dir')
    drops_dir = os.path.join(res_dir, 'drops')
    if not os.path.exists(drops_dir):
        Dodo.run(['mkdir', drops_dir])
    drop_dest_dir = os.path.join(drops_dir, args.package)

    if os.path.exists(drop_dest_dir):
        msg = ''
        msg += 'Target path already exists: %s\n' % drop_dest_dir
        msg += '\nThis probably means that %s has been already dropped into %s.\n' % (
            args.package, res_dir)
        msg += 'To update the drop-in manually, please run:\n\n'
        msg += '%s %s %s' % (_diff_tool(), drop_src_dir, drop_dest_dir)
        raise CommandError(msg)

    Dodo.run(['cp', '-rf', drop_src_dir, drop_dest_dir])

    readme_path = os.path.join(drop_src_dir, 'README.md')
    if os.path.exists(readme_path):
        Dodo.run(['cat', readme_path])
