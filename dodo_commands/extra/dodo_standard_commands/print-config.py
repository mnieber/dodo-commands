import re
from argparse import ArgumentParser

from dodo_commands.dependencies import yaml_round_trip_dump
from dodo_commands.framework.singleton import Dodo


def _args():
    parser = ArgumentParser(description="Print the full configuration.")
    parser.add_argument("key", nargs="?")
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    if args.key:
        prefix = "" if args.key.startswith("/") else "/"
        contents = Dodo.get(prefix + args.key)
        if isinstance(contents, str):
            print(contents)
        else:
            print("%s" % yaml_round_trip_dump(contents))
    else:
        content = re.sub(
            r"^([0-9_A-Z]+\:)$",
            r"\n\1",
            yaml_round_trip_dump(Dodo.get()),
            flags=re.MULTILINE,
        )
        print(re.sub(r"^\n\n", r"\n", content, flags=re.MULTILINE))
