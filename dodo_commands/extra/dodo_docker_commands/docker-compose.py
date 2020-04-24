from dodo_commands import Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.config import expand_keys


def _args():
    Dodo.parser.description = "Run docker compose"

    Dodo.parser.add_argument("compose_args", nargs="*")
    args = Dodo.parse_args()
    args.cwd = Dodo.get_config("/DOCKER_COMPOSE/cwd")
    args.file = Dodo.get_config("/DOCKER_COMPOSE/file", None)
    args.map = Dodo.get_config("/DOCKER_COMPOSE/map", {})
    args.compose_project_name = Dodo.get_config(
        "/DOCKER_COMPOSE/compose_project_name", Dodo.get_config("/ROOT/env_name")
    )
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()

    for src, dest in args.map.items():
        with open(src) as ifs:
            content = expand_keys(Dodo.get_config(), ifs.read())
        with open(dest, "w") as ofs:
            ofs.write(content)

    file_args = ["-f", args.file] if args.file else []
    with plumbum.local.env(COMPOSE_PROJECT_NAME=args.compose_project_name):
        Dodo.run(["docker-compose", *file_args, *args.compose_args], cwd=args.cwd)
