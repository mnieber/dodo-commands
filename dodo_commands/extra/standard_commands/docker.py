"""This command opens a bash shell in the docker container."""
from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'service',
            choices=self.get_config('/DOCKER/options', {}).keys(),
            nargs='?',
            help=("Use this key to look up the docker image in /DOCKER/options")
        )
        parser.add_argument(
            '--image',
            choices=self.get_config('/DOCKER/images', {}).keys(),
            help=("Use the docker image stored under this key in /DOCKER/images")
        )
        parser.add_argument(
            '--name',
            help=("Override the name of the started docker container")
        )
        parser.add_argument('--command', default='/bin/bash')

    def _get_docker_options(self, command_name):
        return self.get_config('/DOCKER', {}) \
            .setdefault('options', {}) \
            .setdefault(command_name, {})

    def handle_imp(self, service, image, name, command, **kwargs):  # noqa
        if service:
            self.get_config('/DOCKER', {}) \
                .setdefault('aliases', {}) \
                .setdefault('docker', service)
        else:
            service = self.name

        if image:
            docker_image = self.get_config(
                '/DOCKER/images/%s/image' % image,
                image
            )
            self._get_docker_options(service)['image'] = docker_image

        if name:
            self._get_docker_options(service)['name'] = name

        self.runcmd(
            ["/bin/bash"] + (["-c", command] if command else []),
            cwd=self.get_config("/DOCKER/default_cwd", "/"))
