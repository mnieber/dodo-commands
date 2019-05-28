from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import bash_cmd


def _args():
    parser = ArgumentParser()
    parser.add_argument('--name')
    args = Dodo.parse_args(parser)
    args.name = args.name or 'dodo'
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    tmp_filename = '/tmp/%s_autocomplete.sh' % args.name
    Dodo.run(
        bash_cmd(
            'register-python-argcomplete %s > %s' % (args.name, tmp_filename)))
    Dodo.run([
        'sudo', 'mv', tmp_filename,
        '/etc/bash_completion.d/%s_autocomplete.sh' % args.name
    ])
