from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.util import remove_trailing_dashes
import argparse
import os


def _dodo_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'name',
        choices=Dodo.get_config('/DOCKER/images').keys(),
        help='Key to look up in /DOCKER/images')
    parser.add_argument(
        'build_args',
        nargs=argparse.REMAINDER,
        help='Extra args to pass to docker build')
    return Dodo.parse_args(parser)


def _convert_dodo_args():
    dodo_args = _dodo_args()
    gc = Dodo.create_get_config(dodo_args.__dict__)
    args = argparse.Namespace()
    args.build_dir = gc(key='/DOCKER/images/{name}/build_dir', default='.')
    args.docker_file = gc(
        key='/DOCKER/images/{name}/docker_file', default='Dockerfile')
    args.extra_dirs = gc(key='/DOCKER/images/{name}/extra_dirs', default=[])
    args.docker_image = gc(key='/DOCKER/images/{name}/image')
    args.build_args = dodo_args.build_args
    return args


def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-dir', default='.')
    parser.add_argument('--docker-filename', default='Dockerfile')
    parser.add_argument('--extra_dir', action='append', dest='extra_dirs')
    parser.add_argument('docker_image')
    parser.add_argument('build_args', nargs=argparse.REMAINDER)
    return Dodo.parse_args(parser)


def _copy_extra_dirs(local_dir, extra_dirs):
    # todo: convert extra dirs config mapping into a list of key=val
    for extra_dir in (extra_dirs or []):
        extra_dir_name, extra_dir_path = extra_dir.split('=')
        local_path = os.path.join(local_dir, extra_dir_name)
        if os.path.exists(local_path):
            raise CommandError("Cannot copy to existing path: " + local_path)
        if not os.path.exists(extra_dir_path):
            raise CommandError("Cannot copy from non-existing path: " +
                               extra_dir_path)
        Dodo.run(['cp', '-rf', extra_dir_path, local_path])


def _remove_extra_dirs(local_dir, extra_dirs):
    for extra_dir in (extra_dirs or []):
        extra_dir_name, extra_dir_path = extra_dir.split('=')
        local_path = os.path.join(local_dir, extra_dir_name)
        Dodo.run(['rm', "rm", "-rf", local_path])


args = (_convert_dodo_args() if Dodo.command_name else _args())

if Dodo.is_main(__name__, safe=len(args.extra_dirs) == 0):
    _copy_extra_dirs(args.build_dir, args.extra_dirs)

    try:
        Dodo.run(
            [
                "docker",
                "build",
                "-t",
                args.docker_image,
                "-f",
                args.docker_file,
            ] + remove_trailing_dashes(args.build_args) + [
                ".",
            ],
            cwd=args.build_dir)
    finally:
        _remove_extra_dirs(args.build_dir, args.extra_dirs)
