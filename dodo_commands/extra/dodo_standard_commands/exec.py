from dodo_commands import Dodo


def _args():
    Dodo.parser.description = "Run something on the commandline"

    Dodo.parser.add_argument("--cwd")
    Dodo.parser.add_argument("script_args", nargs="*")

    args = Dodo.parse_args()
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(args.script_args, cwd=args.cwd or None)
