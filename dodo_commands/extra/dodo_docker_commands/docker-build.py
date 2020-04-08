import argparse
import os

from dodo_commands import CommandError, Dodo, remove_trailing_dashes


def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument('name',
                        choices=Dodo.get_config('/DOCKER_IMAGES').keys(),
                        help='Key to look up in /DOCKER_IMAGES')
    parser.add_argument('build_args',
                        nargs=argparse.REMAINDER,
                        help='Extra args to pass to docker build')
    args = Dodo.parse_args(parser)
    args.build_dir = Dodo.get_config(
        '/DOCKER_IMAGES/{name}/build_dir'.format(name=args.name), '.')
    args.docker_file = Dodo.get_config(
        '/DOCKER_IMAGES/{name}/docker_file'.format(name=args.name),
        'Dockerfile')
    args.extra_dirs = Dodo.get_config(
        '/DOCKER_IMAGES/{name}/extra_dirs'.format(name=args.name), [])
    args.docker_image = Dodo.get_config(
        '/DOCKER_IMAGES/{name}/image'.format(name=args.name))
    return args


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
        if (os.path.abspath(local_dir).startswith(
                os.path.abspath(extra_dir_path))):
            rp = os.path.relpath(local_dir, extra_dir_path)
            dead_path = os.path.join(local_path, rp)
            if os.path.exists(dead_path):
                Dodo.run(['rm', '-rf', dead_path])


def _remove_extra_dirs(local_dir, extra_dirs):
    for extra_dir in (extra_dirs or []):
        extra_dir_name, extra_dir_path = extra_dir.split('=')
        local_path = os.path.join(local_dir, extra_dir_name)
        Dodo.run(['rm', "-rf", local_path])


if Dodo.is_main(__name__):
    args = _args()
    Dodo.safe = len(args.extra_dirs) == 0

    _copy_extra_dirs(args.build_dir, args.extra_dirs)

    try:
        Dodo.run([
            "docker",
            "build",
            "-t",
            args.docker_image,
            "-f",
            args.docker_file,
        ] + remove_trailing_dashes(args.build_args) + [
            ".",
        ],
                 cwd=args.build_dir)  # noqa
    finally:
        _remove_extra_dirs(args.build_dir, args.extra_dirs)
