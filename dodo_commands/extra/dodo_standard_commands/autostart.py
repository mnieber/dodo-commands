import os
from argparse import ArgumentParser

from dodo_commands import Dodo


def _args():
    parser = ArgumentParser(
        description=(
            "Writes (or removes) a small script that activates the latest "
            + "Dodo Commands project"
        )
    )
    parser.add_argument("status", choices=["on", "off"])
    return Dodo.parse_args(parser)


if Dodo.is_main(__name__, safe=False):
    args = _args()

    for shell, activate_cmd in (
        ("bash", "$(dodo env --latest --shell=bash) &&"),
        ("fish", "eval (dodo env --latest --shell=fish); and"),
    ):

        confd_dir = os.path.expanduser("~/.config/%s/conf.d" % shell)
        if not os.path.exists(confd_dir):
            Dodo.run(["mkdir", "-p", confd_dir])
        script = os.path.join(confd_dir, "dodo_autostart." + shell)
        if args.status == "on" and not os.path.exists(script):
            with open(script, "w") as f:
                f.write("# NOTE: automatically generated file, don't edit.\n")
                f.write("%s dodo check-version --dodo --config\n" % activate_cmd)
        if args.status == "off" and os.path.exists(script):
            os.unlink(script)
