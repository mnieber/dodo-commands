from argparse import ArgumentParser
from dodo_commands.framework import Dodo, DecoratorScope
from dodo_standard_commands.decorators.docker import (Decorator as
                                                      DockerDecorator)


def _choices():
    choices = []
    for key in Dodo.get_config('/DOCKER/options', {}).keys():
        keys = [key] if isinstance(key, str) else key
        for x in keys:
            if x not in choices and not x.startswith('!'):
                choices.append(str(x))
    return choices


def _args():
    parser = ArgumentParser(
        description='Opens a bash shell in the docker container.')
    parser.add_argument(
        'service',
        choices=_choices(),
        help=("Use this key to look up the docker options in /DOCKER/options"))
    parser.add_argument(
        '--image',
        choices=Dodo.get_config('/DOCKER/images', {}).keys(),
        help=("Use the docker image stored under this key in /DOCKER/images"))
    parser.add_argument(
        '--image-name', help=("Use the docker image with this name"))
    parser.add_argument(
        '--name', help=("Override the name of the started docker container"))
    parser.add_argument('--command')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()

    docker_options = DockerDecorator.merged_options(Dodo.get_config,
                                                    args.service)

    if args.image:
        docker_options['image'] = Dodo.get_config(
            '/DOCKER/images/%s/image' % args.image, args.image)
    elif args.image_name:
        docker_options['image'] = args.image_name

    if args.name:
        docker_options['name'] = args.name
    else:
        docker_options['name'] = args.service

    Dodo.get_config('/DOCKER')['options'] = {Dodo.command_name: docker_options}

    with DecoratorScope('docker'):
        Dodo.run(
            ["/bin/bash"] + (["-c", args.command] if args.command else []),
            cwd=docker_options.get("cwd", "/"))
