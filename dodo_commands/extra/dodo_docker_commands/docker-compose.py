from dodo_commands import Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.config import expand_keys


def _args():
    Dodo.parser.description = "Run docker compose"

    Dodo.parser.add_argument("compose_args", nargs="*")
    Dodo.parser.add_argument("--detach", action="store_true")
    args = Dodo.parse_args()
    args.cwd = Dodo.get("/DOCKER_COMPOSE/cwd")
    args.files = Dodo.get("/DOCKER_COMPOSE/files", None)
    args.map = Dodo.get("/DOCKER_COMPOSE/map", {})
    args.compose_project_name = Dodo.get(
        "/DOCKER_COMPOSE/compose_project_name", Dodo.get("/ROOT/env_name")
    )
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()

    for src, dest in args.map.items():
        with open(src) as ifs:
            content = expand_keys(Dodo.get(), ifs.read())
        with open(dest, "w") as ofs:
            ofs.write(content)

    def get_file_args():
        result = []
        for f in args.files:
            result.extend(["--file", f])
        return result

    file_args = get_file_args() if args.files else []
    detach_args = ["--detach"] if args.detach else []
    with plumbum.local.env(COMPOSE_PROJECT_NAME=args.compose_project_name):
        Dodo.run(
            ["docker-compose", *file_args, *args.compose_args, *detach_args],
            cwd=args.cwd,
        )
