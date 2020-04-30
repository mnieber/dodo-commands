import os

from dodo_commands import Dodo


def _args():
    Dodo.parser.add_argument("number")
    args = Dodo.parse_args()
    args.dirs = Dodo.get("/DIAL", [])
    return args


if Dodo.is_main(__name__):
    args = _args()
    dial_dir = os.path.expanduser(os.path.expandvars(args.dirs[int(args.number)]))
    print("cd %s" % dial_dir)
