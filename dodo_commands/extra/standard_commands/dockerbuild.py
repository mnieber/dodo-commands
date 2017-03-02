"""Build a docker image."""

import os

from . import DodoCommand
from dodo_commands.framework import CommandError


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            '--image',
            dest="docker_image",
            help=(
                "Identifies the docker image. "
                "You should supply a value foo:bar. "
                "A file Dockerfile.foo.bar will be used "
                "as the input docker file."
            )
        )

    def _copy_extra_dirs(self, local_dir, extra_dirs):
        for extra_dir_name, extra_dir_path in extra_dirs.items():
            local_path = os.path.join(local_dir, extra_dir_name)
            if os.path.exists(local_path):
                raise CommandError(
                    "Cannot copy to existing path: " + local_path
                )
            if not os.path.exists(extra_dir_path):
                raise CommandError(
                    "Cannot copy from non-existing path: " + extra_dir_path
                )
            self.runcmd(["cp", "-rf", extra_dir_path, local_path])

    def _remove_extra_dirs(self, local_dir, extra_dirs):
        for extra_dir_name, extra_dir_path in extra_dirs.items():
            local_path = os.path.join(local_dir, extra_dir_name)
            self.runcmd(["rm", "-rf", local_path])

    def handle_imp(self, docker_image, **kwargs):  # noqa
        res_dir = os.path.join(
            self.get_config("/ROOT/project_dir"), "dodo_commands", "res"
        )
        local_dir = self.get_config("/DOCKER/build_dir", res_dir)

        if not docker_image:
            docker_image = self.get_config("/DOCKER/image")

        extra_dirs = self.get_config("/DOCKER/extra_dirs", {})
        self._copy_extra_dirs(local_dir, extra_dirs)

        try:
            self.runcmd(
                [
                    "docker",
                    "build",
                    "-t",
                    docker_image,
                    "-f",
                    "Dockerfile.%s.%s" % tuple(docker_image.split(":", 1)),
                ] +
                [
                    ".",
                ],
                cwd=local_dir
            )
        finally:
            self._remove_extra_dirs(local_dir, extra_dirs)
