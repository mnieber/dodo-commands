from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.config import ConfigIO
from plumbum.cmd import docker


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        'container_type',
        choices=Dodo.get_config('/DOCKER/container_types', {}).keys())
    parser.add_argument('name')
    args = Dodo.parse_args(parser)
    args.dirs = Dodo.get_config(
        "/DOCKER/container_types/%s/dirs" % args.container_type)
    args.image = Dodo.get_config(
        "/DOCKER/container_types/%s/image" % args.container_type)
    return args


if Dodo.is_main(__name__, safe=False):
    args = _args()
    existing = docker("ps", "-a", "--quiet", "--filter", "name=" + args.name)
    if not existing:
        cmd_args = [
            "docker",
            "create",
            "--name",
            args.name,
        ]

        for path in args.dirs:
            cmd_args.extend(["-v", path])

        cmd_args.append(args.image)
        Dodo.run(cmd_args)

    config = ConfigIO().load(load_layers=False)
    config['DOCKER'].setdefault('containers',
                                {})[args.container_type] = args.name
    ConfigIO().save(config)
