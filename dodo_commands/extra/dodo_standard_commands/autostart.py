from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import os


def _args():
    parser = ArgumentParser(
        description=(
            "Writes (or removes) a small script that activates the latest " +
            "Dodo Commands project"
        )
    )
    parser.add_argument('status', choices=['on', 'off'])
    return Dodo.parse_args(parser)


if Dodo.is_main(__name__, safe=False):
    args = _args()

    script = os.path.expanduser("~/.dodo_commands_autostart")
    if args.status == "on" and not os.path.exists(script):
        with open(script, "w") as f:
            f.write("$(dodo activate --latest)\n")
            f.write("dodo check-version --dodo --config\n")
    if args.status == "off" and os.path.exists(script):
        os.unlink(script)
