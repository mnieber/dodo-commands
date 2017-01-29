"""Pull the latest version of the Dodo Commands system."""

from . import DodoCommand
import glob
import os
import shutil
import sys


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('clone_dir')
        parser.add_argument('project_defaults_dir')
        parser.add_argument('--git-url', dest='git_url')
        parser.add_argument(
            '--depth',
            type=int,
            default=0,
            help="Depth for cloning repositories"
        )
        parser.add_argument(
            '--branch',
            help="Branch to checkout after cloning"
        )

    def _report(self, msg):
        sys.stderr.write(msg + "\n")

    def _copy_defaults(self, project_defaults_dir):
        res_dir = os.path.join(self.project_dir, "dodo_commands", "res")
        for filename in glob.glob(os.path.join(project_defaults_dir, "*")):
            dest_path = os.path.join(res_dir, os.path.basename(filename))
            if os.path.isdir(filename):
                shutil.copytree(filename, dest_path)
            else:
                shutil.copy(filename, dest_path)

    def _clone(self, clone_dir, git_url, depth, branch):
        if os.path.exists(clone_dir):
            print("Path already exists, not cloning into: " + clone_dir)
        else:
            self.runcmd(
                [
                    "git",
                    "clone",
                    git_url,
                    os.path.basename(clone_dir)
                ] + (["--depth", depth] if depth else []),
                cwd=os.path.dirname(clone_dir)
            )
            if branch:
                self.runcmd(
                    [
                        "git",
                        "checkout",
                        branch
                    ],
                    cwd=clone_dir
                )

        return True

    def _create_symlink(self, project_defaults_dir):
        target_dir = os.path.join(
            self.project_dir,
            "dodo_commands/default_project"
        )
        if os.path.exists(target_dir):
            os.unlink(target_dir)
        os.symlink(project_defaults_dir, target_dir)

    def handle_imp(
        self, clone_dir, project_defaults_dir, git_url, depth, branch, **kwargs
    ):  # noqa
        self.project_dir = self.get_config('/ROOT/project_dir')
        clone_dir = os.path.join(self.project_dir, clone_dir)
        project_defaults_dir = os.path.join(
            clone_dir, project_defaults_dir
        )

        if git_url:
            self._clone(clone_dir, git_url, depth, branch)

        if not os.path.exists(project_defaults_dir):
            self._report(
                "Default project location %s not " +
                "found." % project_defaults_dir
            )
            return None

        self._create_symlink(project_defaults_dir)

        if git_url:
            self._copy_defaults(project_defaults_dir)
