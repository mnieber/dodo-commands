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
    def _get_docker_volumes_from_list(cls, get_config, prefix=""):
        volumes_from_list = get_config('DOCKER/volumes_from_list', [])
        return (
            [prefix + "%s" % x for x in volumes_from_list]
        )

    @classmethod
    def _get_docker_variable_list(cls, get_config, prefix=""):
        variable_list = get_config('/DOCKER/variable_list', [])
        variable_map = get_config('/ENVIRONMENT/variable_map', {})
        variable_map.update(get_config('/DOCKER/variable_map', []))

        return (
            [prefix + "%s" % x for x in variable_list] +
            [
                prefix + "%s=%s" % key_val
                for key_val in variable_map.items()
            ]
        )

    @classmethod
    def _get_linked_container_list(cls, get_config, prefix=""):
        return [prefix + "%s" % x for x in get_config('/DOCKER/link_list', [])]

    @classmethod
    def get_docker_args(cls, get_config, extra_options):
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
            extra_options +
            cls._get_docker_variable_list(get_config, '--env=') +
            cls._get_docker_volume_list(get_config, '--volume=') +
            cls._get_docker_volumes_from_list(get_config, '--volumes-from=') +
            cls._get_linked_container_list(get_config, '--link=') +
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
        is_enabled = decorated.get_config('/DOCKER/enabled', False)
        if is_enabled == "False" or not is_enabled:
            return args, cwd

        extra_options = []
        if not decorated.opt_non_interactive:
            extra_options.extend(['-i', '-t'])
        if cwd:
            extra_options.extend(['-w', cwd])
        if hasattr(decorated, "docker_options"):
            extra_options.extend(decorated.docker_options)

        new_args = (
            ['docker'] +
            self.get_docker_args(decorated.get_config, extra_options) +
            args
        )
        return new_args, local.cwd
