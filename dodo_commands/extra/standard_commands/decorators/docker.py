"""Decorates command lines with docker arguments."""

from plumbum import local
from dodo_commands.framework import CommandError
from fnmatch import fnmatch


class Decorator:  # noqa
    @classmethod
    def _get_docker_volume_list(cls, docker_config, prefix=""):
        volume_list = docker_config.get('volume_list', [])
        volume_map = docker_config.get('volume_map', {})

        return (
            [prefix + "%s:%s" % (x, x) for x in volume_list] +
            [prefix + "%s:%s" % key_val for key_val in volume_map.items()]
        )

    @classmethod
    def _get_docker_volumes_from_list(cls, docker_config, prefix=""):
        volumes_from_list = docker_config.get('volumes_from_list', [])
        return (
            [prefix + "%s" % x for x in volumes_from_list]
        )

    @classmethod
    def _get_docker_variable_list(cls, docker_config, prefix=""):
        variable_list = docker_config.get('variable_list', [])
        variable_map = docker_config.get('variable_map', {})

        return (
            [prefix + "%s" % x for x in variable_list] +
            [
                prefix + "%s=%s" % key_val
                for key_val in variable_map.items()
            ]
        )

    @classmethod
    def _get_linked_container_list(cls, docker_config, prefix=""):
        return [prefix + "%s" % x for x in docker_config.get('link_list', [])]

    @classmethod
    def get_docker_args(cls, get_config, option_list):
        """
        Get docker args.

        The docker args precede the command which is run
        inside the docker.
        """
        return (
            [
                'run',
            ] +
            option_list +
            [
                get_config('/DOCKER/image'),
            ]
        )

    @classmethod
    def _config_docker_options(cls, get_config, name):
        result = [
            "--env=%s=%s" % key_val
            for key_val in get_config('/ENVIRONMENT/variable_map', {}).items()
        ]

        for pattern, docker_config in get_config('/DOCKER/options', {}).items():
            if fnmatch(name, pattern):
                result.extend(
                    cls._get_docker_variable_list(docker_config, '--env=') +
                    cls._get_docker_volume_list(docker_config, '--volume=') +
                    cls._get_docker_volumes_from_list(docker_config, '--volumes-from=') +
                    cls._get_linked_container_list(docker_config, '--link=') +
                    docker_config.get('extra_options', [])
                )
        return result

    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help="Run docker calls without -i and -t"
        )

    def handle(self, decorated, non_interactive, **kwargs):  # noqa
        decorated.opt_non_interactive = non_interactive

    @classmethod
    def _options(cls, decorated, cwd):
        result = []

        if not hasattr(decorated, 'docker_rm') or decorated.docker_rm:
            result.append(('rm', None))
        if not decorated.opt_non_interactive:
            result.append(('interactive', None))
            result.append(('tty', None))
        if cwd:
            result.append(('workdir', cwd))
        if hasattr(decorated, "docker_options"):
            for p in decorated.docker_options:
                try:
                    key, val = p
                except:
                    raise CommandError(
                        "Elements of docker_options must be tuples of type (key, val)"
                    )
                result.append(p)
        return result

    @classmethod
    def _options_to_list(cls, options):
        return [
            '--%s' % key if val is None else '--%s=%s' % (key, val)
            for key, val in options
        ]

    @classmethod
    def _container_name(cls, options):
        for key, val in options:
            if key == 'name':
                return val
        return ""

    def modify_args(self, decorated, args, cwd):  # noqa
        is_enabled = decorated.get_config('/DOCKER/enabled', False)
        if is_enabled == "False" or not is_enabled:
            return args, cwd

        options = self._options(decorated, cwd)
        new_args = (
            ['docker'] +
            self.get_docker_args(
                decorated.get_config,
                (
                    self._options_to_list(options) +
                    self._config_docker_options(
                        decorated.get_config,
                        self._container_name(options)
                    )
                ),
            ) +
            args
        )
        return new_args, local.cwd
