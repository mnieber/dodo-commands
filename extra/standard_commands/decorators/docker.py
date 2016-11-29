"""Decorates command lines with docker arguments."""

from plumbum import local


class Decorator:  # noqa
    @classmethod
    def _get_docker_volume_list(cls, get_config, prefix=""):
        volume_list = get_config('DOCKER/volume_list', [])
        volume_map = get_config('/DOCKER/volume_map', {})
        return (
            [prefix + "%s:%s" % (x, x) for x in volume_list] +
            [prefix + "%s:%s" % key_val for key_val in volume_map.items()]
        )

    @classmethod
    def _get_docker_variable_list(cls, get_config, prefix=""):
        variable_list = get_config('/DOCKER/variable_list', [])
        variable_map = get_config('/ENVIRONMENT/variable_map', {})
        return (
            [prefix + "%s" % x for x in variable_list] +
            [
                prefix + "%s=%s" % key_val
                for key_val in variable_map.items()
            ]
        )

    @classmethod
    def get_docker_args(cls, get_config, cwd, is_interactive):
        """
        Get docker args.

        The docker args precede the command which is run
        inside the docker.
        """
        return (
            [
                'run',
                '--rm',
            ] +
            (['-w', cwd] if cwd else []) +
            (['-i', '-t'] if is_interactive else []) +
            cls._get_docker_variable_list(get_config, '--env=') +
            cls._get_docker_volume_list(get_config, '--volume=') +
            get_config('/DOCKER/extra_options', []) +
            [
                get_config('/DOCKER/image'),
            ]
        )

    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help="Run docker calls without -i and -t"
        )

    def handle(self, decorated, non_interactive, **kwargs):  # noqa
        decorated.opt_non_interactive = non_interactive

    def modify_args(self, decorated, args, cwd):  # noqa
        if not decorated.get_config('/DOCKER/enabled', False):
            return args, cwd

        new_args = (
            ['docker'] +
            self.get_docker_args(
                decorated.get_config, cwd, not decorated.opt_non_interactive
            ) +
            args
        )
        return new_args, local.cwd
