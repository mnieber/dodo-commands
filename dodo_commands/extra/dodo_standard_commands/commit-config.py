import os

from dodo_commands import Dodo
from dodo_commands.framework.config import Paths


def _args():
    Dodo.parser.add_argument("--alt", help="Run an alternative git command")
    Dodo.parser.add_argument(
        "--message", "-m", dest="message", help="The commit message"
    )
    args = Dodo.parse_args()
    args.cwd = Paths().config_dir()
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.alt:
        Dodo.run(["git", *args.alt.split()], cwd=args.cwd)
    else:
        if not os.path.exists(os.path.join(args.cwd, ".git")):
            Dodo.run(["git", "init"], cwd=args.cwd)

        Dodo.run(["git", "add", "-A"], cwd=args.cwd)
        Dodo.run(
            ["git", "commit", "-m", args.message or "Update configuration"],
            cwd=args.cwd,
        )
