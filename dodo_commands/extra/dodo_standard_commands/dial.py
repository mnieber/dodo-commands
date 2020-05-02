import os

from dodo_commands import Dodo


def _args():
    Dodo.parser.add_argument("number")
    Dodo.parser.add_argument("--group", "-g", default="default")
    args = Dodo.parse_args()
    args.dirs = Dodo.get("/DIAL", {})
    return args


if Dodo.is_main(__name__):
    args = _args()
    dirs = args.dirs[args.group] if args.group else args.dirs

    for k, v in dirs.items():
        if args.number == str(k):
            dial_dir = os.path.expanduser(os.path.expandvars(v))
            print(dial_dir)
