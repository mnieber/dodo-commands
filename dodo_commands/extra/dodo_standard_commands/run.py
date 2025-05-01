import sys

from dodo_commands import Dodo
from dodo_commands.framework.util import maybe_list_to_list


def _args():
    Dodo.parser.add_argument("command")
    Dodo.parser.add_argument("run_args", nargs="*")
    args, more_args = Dodo.parse_args(strict=False)

    return args, more_args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args, more_args = _args()

    commands = {}
    for cmd_name, cmd in Dodo.get("/COMMANDS/list", {}).items():
        if cmd_name.startswith("~"):
            cmd_name = cmd_name[1:]
        commands[cmd_name] = cmd
    if not commands:
        sys.exit(0)

    if args.command not in commands:
        for alias, command in Dodo.get_container().commands.aliases.items():
            if args.command == alias:
                args.command = command
                break

    if args.command not in commands and args.command:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

    command = commands.get(args.command)

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
    is_dodo = cmd == "dodo"

    more_kwargs = {}

    def add_kwarg(kwarg, value):
        cmd_args.append(f"{kwarg}={value}")
        more_kwargs[kwarg] = value

    for arg in args.run_args:
        if arg.startswith("++"):
            if "=" in arg:
                k, v = arg.split("=")
                add_kwarg(k, v)
            else:
                cmd_args.append(arg)
        elif arg.startswith("+"):
            if "=" in arg:
                k, v = arg.split("=")
                add_kwarg(k, v)
            else:
                cmd_args.append(arg)
        else:
            cmd_args.append(arg)

    kwargs = command.get("kwargs", {})
    for kwarg, value in kwargs.items():
        if kwarg not in more_kwargs:
            cmd_args.append(f"{kwarg}={value}")

    cwd = command.get("cwd")

    if env := command.get("env"):
        if isinstance(env, dict):
            env = dict(env)
        else:
            variable_map = {}
            for env_var in env:
                key, value = env_var.split("=")
                variable_map[key] = value
            env = variable_map
        for key, value in env.items():
            if is_dodo:
                cmd_args.append(f"--env={key}={value}")
            else:
                Dodo.get_container().command_line.env_vars_from_input_args.append(
                    f"{key}={value}"
                )
    cmd_args.extend(more_args)

    quiet = False
    if is_dodo:
        quiet = True
        if cwd:
            cmd_args.append(f"--cwd={cwd}")
            cwd = None
        if Dodo._args.confirm:
            Dodo._args.confirm = 0
            cmd_args.append("--confirm")
        for decorator_name in decorator_names:
            cmd_args.append(f"--decorator={decorator_name}")
    else:

        def update_cmd_arg(arg):
            if arg.startswith("++"):
                return f"--{arg[2:]}"
            elif arg.startswith("+"):
                return f"-{arg[1:]}"
            return arg

        cmd_args = [update_cmd_arg(arg) for arg in cmd_args]
        for decorator_name in decorator_names:
            Dodo.get_container().command_line.decorators_from_input_args.append(
                decorator_name
            )

    Dodo.run([cmd, *cmd_args], quiet=quiet, cwd=cwd)
