"""This command opens a bash shell in the docker container."""

from . import DodoCommand


class Command(DodoCommand):  # noqa
    docker_options = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('command', nargs='?')
        parser.add_argument('--name')

    def handle_imp(self, command, name, **kwargs):  # noqa
        if name:
            self.docker_options.append(
                ('name', name)
            )

        self.runcmd(
            ["/bin/bash"] + (["-c", command] if command else []),
            cwd=self.get_config("/DOCKER/default_cwd", None))
