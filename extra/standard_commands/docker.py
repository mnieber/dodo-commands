"""This command opens a bash shell in the docker container."""

from . import DodoCommand


class Command(DodoCommand):  # noqa
    decorators = [
        "docker",
    ]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            ['/bin/bash']
        )
