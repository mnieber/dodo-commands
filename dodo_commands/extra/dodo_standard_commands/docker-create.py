from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from plumbum.cmd import docker


def _args():
    parser = ArgumentParser()
    parser.add_argument('container_type',
                        choices=Dodo.get_config('/DOCKER/container_types',
                                                {}).keys())
    parser.add_argument('name')
    parser.add_argument('--replace',
                        action='store_true',
                        help='Replace existing container')
    args = Dodo.parse_args(parser)
    args.dirs = Dodo.get_config("/DOCKER/container_types/%s/dirs" %
                                args.container_type)
    args.image = Dodo.get_config("/DOCKER/container_types/%s/image" %
                                 args.container_type)
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    existing = docker("ps", "-a", "--quiet", "--filter", "name=" + args.name)

    if existing and args.replace:
        Dodo.run(['docker', 'rm', args.name])

    if not existing or args.replace:
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

    Dodo.runcmd([
        'dodo', 'edit-config',
        '--key=/DOCKER/containers/%s' % args.container_type,
        '--val=%s' % args.name
    ])
