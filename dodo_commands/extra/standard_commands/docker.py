"""This command opens a bash shell in the docker container."""

from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('command', nargs='?')

    def handle_imp(self, command, **kwargs):  # noqa
        self.runcmd(
            ["/bin/bash"] + (["-c", command] if command else []),
            cwd=self.get_config("/DOCKER/default_cwd", None))
