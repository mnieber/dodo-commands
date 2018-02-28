"""This command opens a bash shell in the docker container."""
from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('command', nargs='?')
        parser.add_argument('--name')

    def handle_imp(self, command, name, **kwargs):  # noqa
        options = dict(
            self.get_config('/DOCKER/options/%s' % name, {})
        )
        options['name'] = name
        self.config['DOCKER']['options'].setdefault('docker', options)

        self.runcmd(
            ["/bin/bash"] + (["-c", command] if command else []),
            cwd=self.get_config("/DOCKER/default_cwd", None))
