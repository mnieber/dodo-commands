import sys

from dodo_commands import Dodo
from dodo_commands.framework.util import maybe_list_to_list


def _args():
    Dodo.parser.add_argument("command")
    Dodo.parser.add_argument("run_args", nargs="*")
    args = Dodo.parse_args()

    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()

    commands = Dodo.get("/COMMANDS")
    if not commands:
        sys.exit(0)

    if args.command not in commands:
        for alias, command in Dodo.get_container().commands.aliases.items():
            if args.command == alias:
                args.command = command
                break

    command = commands[args.command]

    cmd = None
    cmd_args = []
    decorator_names = []
    for part in command.get("run", {}):
        # check if part is a dict
        if isinstance(part, dict) and "in" in part:
            for decorator_name in maybe_list_to_list(part["in"]):
                decorator_names.append(decorator_name)
        elif isinstance(part, dict) and "cmd" in part:
            cmd = part["cmd"]
        elif not isinstance(part, dict):
            cmd_args.append(part)
        else:
            raise Exception("Unknown part in command")
    if not cmd:
        raise Exception("No cmd found in command")

    more_kwargs = {}
    more_args = []
    for arg in args.run_args:
        if arg.startswith("++"):
            if "=" in arg:
                k, v = arg.split("=")
                more_kwargs[k] = v
            else:
                more_args.append(arg)
        elif arg.startswith("+"):
            if "=" in arg:
                k, v = arg.split("=")
                more_kwargs[k] = v
            else:
                more_args.append(arg)
        else:
            more_args.append(arg)

    kwargs = command.get("kwargs", {})
    for kwarg, value in kwargs.items():
        if kwarg not in more_kwargs:
            cmd_args.append(f"{kwarg}={value}")
    for kwarg, value in more_kwargs.items():
        cmd_args.append(f"{kwarg}={value}")
    for arg in more_args:
        cmd_args.append(arg)

    cwd = command.get("cwd")

    variable_map = None
    if env := command.get("env"):
        if isinstance(env, dict):
            variable_map = dict(env)
        else:
            variable_map = {}
            for env_var in env:
                key, value = env_var.split("=")
                variable_map[key] = value

    quiet = False
    if cmd == "dodo":
        quiet = True
        if cwd:
            cmd_args.append(f"--cwd={cwd}")
            cwd = None
        for decorator_name in decorator_names:
            cmd_args.append(f"--decorator={decorator_name}")
        decorator_names = []
        if Dodo._args.confirm:
            Dodo._args.confirm = 0
            cmd_args.append("--confirm")

    Dodo.run(
        [cmd, *cmd_args],
        quiet=quiet,
        cwd=cwd,
        decorator_names=decorator_names,
        variable_map=variable_map,
    )
