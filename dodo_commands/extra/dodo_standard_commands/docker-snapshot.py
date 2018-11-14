from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        'container_type', choices=Dodo.get_config('/DOCKER/containers').keys())
    parser.add_argument('output_dir')
    parser.add_argument('--reverse', action='store_true')
    args = Dodo.parse_args(parser)
    return args


def _docker_run(output_dir, args):
    Dodo.run(
        [
            'docker', 'run', '--rm', '--volumes-from', container_name,
            '--volume',
            '%s:/tmp/docker-snapshot' % output_dir, container_type['image']
        ] + args,
        cwd='.')


if Dodo.is_main(__name__, safe=True):
    args = _args()
    container_name = Dodo.get_config('/DOCKER/containers/' +
                                     args.container_type)

    Dodo.get_config('/DOCKER')['options'].setdefault('docker-snapshot', {})
    Dodo.get_config('/DOCKER')['options']['docker-snapshot'][
        'volumes_from'] = container_name

    container_type = Dodo.get_config('/DOCKER/container_types/' +
                                     args.container_type)
    for path in container_type['dirs']:
        host_output_path = os.path.join(args.output_dir, path[1:])
        docker_output_path = os.path.join('/tmp/docker-snapshot', path[1:])

        if args.reverse:
            _docker_run(
                args.output_dir,
                ['/bin/bash', '-c', 'rm -rf ' + os.path.join(path, '*')])
            _docker_run(args.output_dir, [
                '/bin/bash', '-c',
                'cp -rf %s %s' % (os.path.join(docker_output_path, '*'), path)
            ])
        else:
            if os.path.exists(host_output_path):
                Dodo.run(['rm', '-rf', host_output_path], cwd='.')
            Dodo.run(['mkdir', '-p',
                      os.path.dirname(host_output_path)],
                     cwd='.')
            _docker_run(
                args.output_dir,
                ['cp', '-rf', path,
                 os.path.dirname(docker_output_path)])
