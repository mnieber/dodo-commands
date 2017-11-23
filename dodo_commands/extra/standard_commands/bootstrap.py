"""Pull the latest version of the Dodo Commands system."""

from dodo_commands.system_commands import DodoCommand, CommandError
from dodo_commands.framework.config import ConfigIO
import glob
import os
import sys


class Command(DodoCommand):  # noqa
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'src_dir',
            help="The src directory for the bootstrapped project"
        )
        parser.add_argument(
            'project_defaults_dir',
            help="Location relative to src_dir where the default project config is stored",
        )
        parser.add_argument('--force', dest="use_force", action="store_true")

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--git-url', dest='git_url',
            help="Clone this repository to the src_dir location",
        )
        group.add_argument(
            '--link-dir',
            help="Make the src directory a symlink to this directory",
        )
        group.add_argument(
            '--cookiecutter-url',
            help="Use cookiecutter to create the src_dir location",
        )

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

        parser.add_argument(
            '--src-subdir',
            help="Specify a subdirectory of src_dir to clone into",
        )

    def _report(self, msg):
        sys.stderr.write(msg + "\n")

    def _copy_defaults(self, project_defaults_dir, use_force):
        res_dir = os.path.join(self.project_dir, "dodo_commands", "res")
        for filename in glob.glob(os.path.join(project_defaults_dir, "*")):
            dest_path = os.path.join(res_dir, os.path.basename(filename))
            if os.path.exists(dest_path):
                if self.opt_confirm:
                    print("Warning, destination path already exists: %s" % dest_path)
                elif use_force:
                    print("Overwriting existing path: %s" % dest_path)
                else:
                    raise CommandError(
                        "Destination path %s already exists. " % dest_path +
                        "Use the --confirm or --force flag to overwrite it."
                    )
            self.runcmd(["cp", "-rf", filename, dest_path])

    def _clone(self, src_dir, git_url, depth, branch):
        if os.path.exists(src_dir):
            raise CommandError("Cannot clone into %s, path already exists" % src_dir)

        self.runcmd(
            [
                "git",
                "clone",
                git_url,
                os.path.basename(src_dir)
            ] + (["--depth", depth] if depth else []),
            cwd=os.path.dirname(src_dir)
        )
        if branch:
            self.runcmd(
                [
                    "git",
                    "checkout",
                    branch
                ],
                cwd=src_dir
            )

    def _cookiecutter(self, src_dir, cookiecutter_url):
        if os.path.exists(src_dir):
            raise CommandError("Cannot clone into %s, path already exists" % src_dir)

        self.runcmd(
            [
                "cookiecutter",
                cookiecutter_url,
                "-o", src_dir
            ]
        )

    def _link(self, src_dir, link_dir):
        if os.path.exists(src_dir):
            raise CommandError("Cannot create a link because %s already exists" % src_dir)
        self.runcmd(["ln", "-s", link_dir, src_dir])

    def _create_symlink_to_defaults(self, project_defaults_dir):
        target_dir = os.path.join(
            self.project_dir,
            "dodo_commands/default_project"
        )
        if os.path.exists(target_dir):
            self.runcmd(["rm", target_dir])
        self.runcmd(["ln", "-s", project_defaults_dir, target_dir])

    def _write_src_dir(self, src_dir):
        config = ConfigIO().load(load_layers=False)
        config['ROOT']['src_dir'] = src_dir
        ConfigIO().save(config)

    def _get_full_src_dir(self, src_dir, src_subdir):
        postfix = (
            os.path.join(src_dir, src_subdir)
            if src_subdir else
            src_dir
        )
        return (
            postfix
            if os.path.isabs(src_dir) else
            os.path.join(self.project_dir, postfix)
        )

    def handle_imp(
        self,
        src_dir,
        project_defaults_dir,
        use_force,
        git_url,
        link_dir,
        cookiecutter_url,
        depth,
        branch,
        src_subdir,
        **kwargs
    ):  # noqa
        self.project_dir = self.get_config('/ROOT/project_dir')
        full_src_dir = self._get_full_src_dir(src_dir, src_subdir)
        self.runcmd(['mkdir', '-p', os.path.dirname(full_src_dir)])

        if git_url:
            self._clone(full_src_dir, git_url, depth, branch)
        elif link_dir:
            self._link(full_src_dir, os.path.expanduser(link_dir))
        elif cookiecutter_url:
            self._cookiecutter(full_src_dir, os.path.expanduser(cookiecutter_url))

        project_defaults_dir = os.path.join(full_src_dir, project_defaults_dir)
        if not os.path.exists(project_defaults_dir):
            raise CommandError(
                "Default project location %s not found." % project_defaults_dir
            )

        self._create_symlink_to_defaults(project_defaults_dir)
        self._copy_defaults(project_defaults_dir, use_force)
        self._write_src_dir(
            src_dir
            if os.path.isabs(src_dir) else
            os.path.join("${/ROOT/project_dir}", src_dir)
        )
