"""This command opens a bash shell in the docker container."""
from . import DodoCommand
from dodo_commands.extra.standard_commands.decorators.docker import (
    Decorator as DockerDecorator
)


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'service',
            choices=self.get_config('/DOCKER/options', {}).keys(),
            help=("Use this key to look up the docker options in /DOCKER/options")
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

    def handle_imp(self, service, image, name, command, **kwargs):  # noqa
        docker_options = DockerDecorator.merged_options(
            self.get_config, service
        )

        if image:
            docker_options['image'] = self.get_config(
                '/DOCKER/images/%s/image' % image,
                image
            )

        if name:
            docker_options['name'] = name

        self.get_config('/DOCKER')['options'] = {self.name: docker_options}
        self.runcmd(
            ["/bin/bash"] + (["-c", command] if command else []),
            cwd=docker_options.get("cwd", "/")
        )
