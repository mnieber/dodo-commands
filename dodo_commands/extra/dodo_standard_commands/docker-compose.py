from argparse import ArgumentParser, REMAINDER

from plumbum import local

from dodo_commands import Dodo, remove_trailing_dashes
from dodo_commands.framework.config import expand_keys


def _args():
    parser = ArgumentParser(description='Run docker compose')

    parser.add_argument('compose_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.cwd = Dodo.get_config('/DOCKER_COMPOSE/src_dir')
    args.map = Dodo.get_config('/DOCKER_COMPOSE/map', {})
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()

    for src, dest in args.map.items():
        with open(src) as ifs:
            content = expand_keys(Dodo.get_config(), ifs.read())
        with open(dest, 'w') as ofs:
            ofs.write(content)

    compose_project_name = Dodo.get_config(
        '/DOCKER_COMPOSE/compose_project_name',
        Dodo.get_config('/ROOT/project_name'))
    with local.env(COMPOSE_PROJECT_NAME=compose_project_name):
        Dodo.run(['docker-compose'] +
                 remove_trailing_dashes(args.compose_args),
                 cwd=args.cwd)
