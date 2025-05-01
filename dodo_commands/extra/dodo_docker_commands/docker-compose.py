from dodo_commands import Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.config import expand_keys
from dodo_commands.framework.global_config import load_global_config_parser
from dodo_commands.framework.util import to_arg_list


def _args():
    Dodo.parser.description = "Run docker compose"

    Dodo.parser.add_argument("compose_args", nargs="*")

    group = Dodo.parser.add_mutually_exclusive_group()
    group.add_argument("--cat", action="store_true")
    group.add_argument("--edit", action="store_true")
    args = Dodo.parse_args()

    key = "DOCKER_COMPOSE"
    args.cwd = Dodo.get("/" + key + "/cwd")
    args.progress = Dodo.get("/" + key + "/progress", "plain")
    args.files = Dodo.get("/" + key + "/files", None)
    args.env_file = Dodo.get("/" + key + "/env_file", None)
    args.map = Dodo.get("/" + key + "/map", {})
    args.editor = load_global_config_parser().get("settings", "editor")
    args.compose_project_name = Dodo.get(
        "/" + key + "/compose_project_name", Dodo.get("/ROOT/env_name")
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
    env_file_args = [f"--env-file={args.env_file}"] if args.env_file else []

    compose_args = to_arg_list(args.compose_args)
    if "build" in compose_args[:1]:
        if "--progress" not in compose_args:
            compose_args = [
                compose_args[0],
                "--progress",
                args.progress,
                *compose_args[1:],
            ]
    if args.cat:
        for f in args.files:
            Dodo.run(["cat", f], cwd=args.cwd)
    elif args.edit:
        Dodo.run([args.editor, *args.files], cwd=args.cwd)
    else:
        with plumbum.local.env(COMPOSE_PROJECT_NAME=args.compose_project_name):
            Dodo.run(
                [
                    "docker",
                    "compose",
                    *file_args,
                    *env_file_args,
                    *compose_args,
                ],
                cwd=args.cwd,
            )
