"""Build a docker image."""

import argparse
import os

from . import DodoCommand
from dodo_commands.framework import CommandError
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'name',
            choices=self.get_config('/DOCKER/images', {}).keys(),
            help='Look the docker image by this name in /DOCKER/images'
        )
        parser.add_argument(
            'build_args',
            nargs=argparse.REMAINDER
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

    def handle_imp(self, name, build_args, **kwargs):  # noqa
        docker_image = self.get_config('/DOCKER/images/%s/image' % name, name)
        docker_file = self.get_config(
            '/DOCKER/images/%s/docker_file' % name,
            "Dockerfile"
        )
        build_dir = self.get_config("/DOCKER/images/%s/build_dir" % name)
        extra_dirs = self.get_config("/DOCKER/images/%s/extra_dirs" % name, {})
        self._copy_extra_dirs(build_dir, extra_dirs)

        try:
            self.runcmd(
                [
                    "docker",
                    "build",
                    "-t",
                    docker_image,
                    "-f",
                    docker_file,
                ] + remove_trailing_dashes(build_args) +
                [
                    ".",
                ],
                cwd=build_dir
            )
        finally:
            self._remove_extra_dirs(build_dir, extra_dirs)
