import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum, six
from dodo_commands.framework.choice_picker import ChoicePicker
from dodo_commands.framework.util import query_yes_no

docker = plumbum.cmd.docker
raw_input = six.moves.input


def _container_type_names():
    return list(Dodo.get("/DOCKER/container_types", {}).keys())


def _args():
    parser = ArgumentParser()
    parser.add_argument("container_type", choices=_container_type_names(), nargs="?")
    parser.add_argument("name", nargs="?")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--interactive", "-i", action="store_true")
    group.add_argument(
        "--replace", action="store_true", help="Replace existing container"
    )

    args = Dodo.parse_args(parser)
    args.container_types = Dodo.get("/DOCKER/container_types")
    args.env_name = Dodo.get("/ROOT/env_name")

    return args


def _exists(name):
    return docker("ps", "-a", "--quiet", "--filter", "name=" + name)


def _create_container(container_types, container_type_name, name, replace):
    dirs = container_types.get(container_type_name, {})["dirs"]
    image = container_types.get(container_type_name, {})["image"]

    exists = _exists(name)

    if exists and replace:
        Dodo.run(["docker", "rm", name])

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


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.interactive:

        class Picker(ChoicePicker):
            def print_choices(self, choices):
                for idx, container_type in enumerate(choices):
                    print("%d - %s" % (idx + 1, container_type))

            def question(self):
                return "Select a container type: "

        picker = Picker(_container_type_names())
        picker.pick()

        for container_type_name in picker.get_choices():
            default_container_name = "dc_%s_%s" % (args.env_name, container_type_name)
            name = (
                raw_input(
                    "Enter a name for container type %s [%s]: "
                    % (container_type_name, default_container_name)
                )
                or default_container_name
            )

            if _exists(name):
                replace = query_yes_no(
                    "A container with this name exists. "
                    + "To replace choose yes. To quit choose no. Replace it?"
                )
                if not replace:
                    sys.exit(0)

            _create_container(
                args.container_types, container_type_name, name, replace=True
            )
    else:
        if not args.container_type:
            raise CommandError("Argument container_type is required")
        if not args.name:
            raise CommandError("Argument name is required")
        _create_container(
            args.container_types, args.container_type, args.name, args.replace
        )
