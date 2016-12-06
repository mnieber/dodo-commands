"""Build a docker image."""

import os

from . import DodoCommand


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'docker_image',
            help=(
                "Identifies the docker image. "
                "You should supply a value foo:bar. "
                "A file Dockerfile.foo.bar will be used "
                "as the input docker file."
            )
        )

        parser.add_argument(
            '--build-arg'
        )

    def handle_imp(self, docker_image, build_arg, **kwargs):  # noqa
        commands_dir = os.path.join(
            self.get_config("/ROOT/project_dir"), "dodo_commands"
        )

        self.runcmd(
            [
                "docker",
                "build",
                "-t",
                docker_image,
                "-f",
                "Dockerfile.%s.%s" % tuple(docker_image.split(":", 1)),
            ] +
            (
                ["--build-arg", build_arg]
                if build_arg else
                []
            ) +
            [
                ".",
            ],
            cwd=self.get_config("/DOCKER/build_dir", commands_dir)
        )
