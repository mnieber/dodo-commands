from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import os
import glob


def _args():
    parser = ArgumentParser()
    parser.add_argument('where')
    parser.add_argument('what')
    parser.add_argument('--pattern', default='*')
    parser.add_argument('--replace')
    args = Dodo.parse_args(parser)
    return args


def _replace(where, what, replace_with):
    for filepath in glob.iglob(
            os.path.join(where, '**/' + args.pattern), recursive=True):
        with open(filepath) as file:
            s = file.read()
        s2 = s.replace(what, replace_with)
        if s != s2:
            with open(filepath, "w") as file:
                file.write(s2)


args = _args()
if Dodo.is_main(__name__, safe=not args.replace):
    if args.replace:
        _replace(args.where, args.what, args.replace)
    else:
        Dodo.run(['grep', '-rnw', args.where, '-e', "'{}'".format(args.what)])
