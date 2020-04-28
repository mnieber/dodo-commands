import os

from dodo_commands import Dodo


def _args():
    Dodo.parser.add_argument(
        "container_type", choices=Dodo.get("/DOCKER/containers").keys()
    )
    Dodo.parser.add_argument("output_dir")
    Dodo.parser.add_argument("--reverse", action="store_true")
    return Dodo.parse_args()


def _docker_run(output_dir, args):
    Dodo.run(
        [
            "docker",
            "run",
            "--rm",
            "--volumes-from",
            container_name,
            "--volume",
            "%s:/tmp/docker-snapshot" % output_dir,
            container_type["image"],
        ]
        + args,
        cwd=".",
    )


if Dodo.is_main(__name__, safe=True):
    args = _args()
    container_name = Dodo.get("/DOCKER/containers/" + args.container_type)

    docker_options = Dodo.get("/DOCKER_OPTIONS", {})
    docker_options.setdefault("docker-snapshot", {})
    docker_options["docker-snapshot"]["volumes_from"] = container_name

    container_type = Dodo.get("/DOCKER/container_types/" + args.container_type)
    for path in container_type["dirs"]:
        host_output_path = os.path.join(args.output_dir, path[1:])
        docker_output_path = os.path.join("/tmp/docker-snapshot", path[1:])

        if args.reverse:
            _docker_run(args.output_dir, ["rm", "-rf", os.path.join(path, "*")])
            _docker_run(
                args.output_dir,
                ["cp", "-rf", os.path.join(docker_output_path, "*"), path],
            )
        else:
            if os.path.exists(host_output_path):
                Dodo.run(["rm", "-rf", host_output_path], cwd=".")
            Dodo.run(["mkdir", "-p", os.path.dirname(host_output_path)], cwd=".")
            _docker_run(
                args.output_dir,
                ["cp", "-rf", path, os.path.dirname(docker_output_path)],
            )
