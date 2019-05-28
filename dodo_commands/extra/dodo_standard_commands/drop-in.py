from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import get_command_path, load_global_config_parser
from dodo_commands.framework.util import chop
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument('package', choices=_drop_dir_by_package_name().keys())
    return Dodo.parse_args(parser)


def _diff_tool():
    return load_global_config_parser().get("settings", "diff_tool")


def _read_dot_drop_path(path):
    with open(path) as ifs:
        base_dir = os.path.realpath(os.path.dirname(path))
        rel_dir = chop(ifs.read())
        return os.path.realpath(os.path.join(base_dir, rel_dir))


def _register_drop_dir(drop_dir_by_package_name, package_name, drop_src_dir):
    if package_name in drop_dir_by_package_name:
        if drop_src_dir == drop_dir_by_package_name[package_name]:
            return
        else:
            print('Warning: Found two drop directories for package %s:\n' %
                  package_name)
            print(drop_src_dir)
            print(drop_dir_by_package_name[package_name])
    drop_dir_by_package_name[package_name] = drop_src_dir


def _dot_drop_path(item):
    result = os.path.join(item, '.drop-in')
    return result if os.path.exists(result) else None


def _drop_src_dir(item):
    result = os.path.join(item, 'drop-in')
    return result if os.path.isdir(result) else None


def _drop_dir_by_package_name():
    drop_dir_by_package_name = {}
    command_path = get_command_path(Dodo.get_config())
    for item in command_path.items:
        dot_drop_path = _dot_drop_path(item)
        default_drop_src_dir = _drop_src_dir(item)

        if not dot_drop_path and not default_drop_src_dir:
            continue

        if dot_drop_path and default_drop_src_dir:
            print("Warning: found two drop-ins where only one was expected:\n")
            print("%s\n%s" % (dot_drop_path, default_drop_src_dir))

        package_name = os.path.basename(item)
        drop_src_dir = default_drop_src_dir or _read_dot_drop_path(
            dot_drop_path)
        _register_drop_dir(drop_dir_by_package_name, package_name,
                           drop_src_dir)

    return drop_dir_by_package_name


if Dodo.is_main(__name__, safe=True):
    args = _args()

    drop_src_dir = _drop_dir_by_package_name().get(args.package)
    if not drop_src_dir:
        raise CommandError("No drop-in found for package %s" % args.package)

    if not os.path.isdir(drop_src_dir):
        raise CommandError(
            "The drop-in directory does not exist: %s" % drop_src_dir)

    res_dir = Dodo.get_config('/ROOT/res_dir')
    drops_target_dir = os.path.join(res_dir, 'drops')
    if not os.path.exists(drops_target_dir):
        Dodo.run(['mkdir', drops_target_dir])
    target_dir = os.path.join(drops_target_dir, args.package)

    if os.path.exists(target_dir):
        msg = ''
        msg += 'Target directory already exists: %s\n' % target_dir
        msg += '\nThis probably means that %s has been already dropped into %s.\n' % (
            args.package, res_dir)
        msg += 'To update the drop-in manually, please run:\n\n'
        msg += '%s %s %s' % (_diff_tool(), drop_src_dir, target_dir)
        raise CommandError(msg)

    Dodo.run(['cp', '-rf', drop_src_dir, target_dir])

    readme_path = os.path.join(drop_src_dir, 'README.md')
    if os.path.exists(readme_path):
        Dodo.run(['cat', readme_path])
