from argparse import ArgumentParser

from dodo_commands import Dodo
from dodo_commands.framework.global_config import load_global_config_parser


def _args():
    parser = ArgumentParser(description="")

    # Parse the arguments.
    args = Dodo.parse_args(parser)

    args.file_browser = load_global_config_parser().get("settings", "file_browser")
    args.project_dir = Dodo.get("/ROOT/project_dir")

    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run([args.file_browser, args.project_dir])
