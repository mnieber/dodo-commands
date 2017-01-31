# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework import call_command
from plumbum import local
from plumbum.cmd import git


class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('branch')

    def handle_imp(self, branch, **kwargs):  # noqa
        src_dir = self.get_config("/ROOT/src_dir")
        with local.cwd(src_dir):
            has_local_changes = git("diff")

        if has_local_changes:
            self.runcmd(
                ["git", "stash", "save", "create_branch_" + branch], cwd=src_dir)
        self.runcmd(["git", "checkout", "dev"], cwd=src_dir)
        self.runcmd(["git", "pull"], cwd=src_dir)
        self.runcmd(["git", "checkout", "-b", branch], cwd=src_dir)
        with local.cwd(src_dir):
            call_command("gitsplit", "--move", "HEAD")
        if has_local_changes:
            self.runcmd(["git", "stash", "pop"], cwd=src_dir)
