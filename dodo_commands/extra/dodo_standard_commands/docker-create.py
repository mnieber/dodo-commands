import sys
from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.util import filter_choices, query_yes_no
from plumbum.cmd import docker
from six.moves import input as raw_input


def _container_type_names():
    return list(Dodo.get_config('/DOCKER/container_types', {}).keys())


def _args():
    parser = ArgumentParser()
    parser.add_argument('container_type',
                        choices=_container_type_names(),
                        nargs='?')
    parser.add_argument('name', nargs='?')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--interactive', '-i', action='store_true')
    group.add_argument('--replace',
                       action='store_true',
                       help='Replace existing container')

    args = Dodo.parse_args(parser)
    args.container_types = Dodo.get_config("/DOCKER/container_types")
    args.project_name = Dodo.get_config('/ROOT/project_name')

    return args


def _exists(name):
    return docker("ps", "-a", "--quiet", "--filter", "name=" + name)


def _create_container(container_types, container_type_name, name, replace):
    dirs = container_types.get(container_type_name, {})['dirs']
    image = container_types.get(container_type_name, {})['image']

    exists = _exists(name)

    if exists and replace:
        Dodo.run(['docker', 'rm', name])

    if not exists or replace:
        cmd_args = [
            "docker",
            "create",
            "--name",
            name,
        ]

        for path in dirs:
            cmd_args.extend(["-v", path])

        cmd_args.append(image)
        Dodo.run(cmd_args)

    Dodo.runcmd([
        'dodo', 'edit-config',
        '--key=/DOCKER/containers/%s' % container_type_name,
        '--val=%s' % name
    ])


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.interactive:
        container_type_names = _container_type_names()
        for idx, container_type in enumerate(container_type_names):
            print('%d - %s' % (idx + 1, container_type))

        raw_choice = raw_input("Select a container type: ")
        selected_container_type_names, span = filter_choices(
            container_type_names, raw_choice)
        if span == [0, len(raw_choice)]:
            for container_type_name in selected_container_type_names:
                default_container_name = 'dc_%s_%s' % (args.project_name,
                                                       container_type_name)
                name = raw_input(
                    "Enter a name for container type %s [%s]: " %
                    (container_type_name,
                     default_container_name)) or default_container_name

                if _exists(name):
                    replace = query_yes_no(
                        'A container with this name exists. ' +
                        'To replace choose yes. To quit choose no. Replace it?'
                    )
                    if not replace:
                        sys.exit(0)

                _create_container(args.container_types,
                                  container_type_name,
                                  name,
                                  replace=True)
        else:
            raise CommandError("Syntax error")

        sys.exit(0)
    else:
        if not args.container_type:
            raise CommandError('Argument container_type is required')
        if not args.name:
            raise CommandError('Argument name is required')
        _create_container(args.container_types, args.container_type, args.name,
                          args.replace)
