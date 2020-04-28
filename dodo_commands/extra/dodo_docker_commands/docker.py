from argparse import ArgumentParser

from dodo_commands import DecoratorScope, Dodo

from dodo_docker_commands.decorators.docker import Decorator as DockerDecorator


def _choices():
    choices = []
    for key in Dodo.get("/DOCKER_OPTIONS", {}).keys():
        keys = [key] if isinstance(key, str) else key
        for x in keys:
            if x not in choices and not x.startswith("!"):
                choices.append(str(x))
    return choices


def _args():
    parser = ArgumentParser(description="Opens a shell in the docker container.")
    parser.add_argument(
        "service",
        choices=_choices(),
        help=("Use this key to look up the docker options in /DOCKER_OPTIONS"),
    )
    parser.add_argument(
        "--image",
        choices=Dodo.get("/DOCKER_IMAGES", {}).keys(),
        help=("Use the docker image stored under this key in /DOCKER_IMAGES"),
    )
    parser.add_argument("--image-name", help=("Use the docker image with this name"))
    parser.add_argument(
        "--name", help=("Override the name of the started docker container")
    )
    parser.add_argument("--command")
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()

    docker_options = DockerDecorator.merged_options(Dodo.get, args.service)

    if args.image:
        docker_options["image"] = Dodo.get(
            "/DOCKER_IMAGES/%s/image" % args.image, args.image
        )
    elif args.image_name:
        docker_options["image"] = args.image_name

    if args.name:
        docker_options["name"] = args.name
    else:
        docker_options["name"] = args.service

    Dodo.get()["DOCKER_OPTIONS"] = {Dodo.command_name: docker_options}

    with DecoratorScope("docker"):
        Dodo.run(
            [args.command] if args.command else ["sh"],
            cwd=docker_options.get("cwd", "/"),
        )
