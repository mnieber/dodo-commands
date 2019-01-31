import ruamel.yaml
import re
from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser(description="Print the full configuration.")
    parser.add_argument('key', nargs='?')
    args = Dodo.parse_args(parser)
    if args.key and args.key.startswith('/'):
        args.key = args.key[1:]
    return args


if Dodo.is_main(__name__):
    args = _args()
    if args.key:
        contents = Dodo.get_config(args.key)
        if isinstance(contents, str):
            print(contents)
        else:
            print("%s" % ruamel.yaml.round_trip_dump(contents))
    else:
        content = re.sub(
            r'^([0-9_A-Z]+\:)$',
            r'\n\1',
            ruamel.yaml.round_trip_dump(Dodo.get_config()),
            flags=re.MULTILINE)
        print(re.sub(r'^\n\n', r'\n', content, flags=re.MULTILINE))
