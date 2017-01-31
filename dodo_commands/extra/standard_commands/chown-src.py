# noqa
from dodo_commands.extra.standard_commands import DodoCommand
import os
from plumbum.cmd import whoami


class Command(DodoCommand):  # noqa
    help = "Changes the owner of ${/ROOT/src_dir} to `whoami`:`whoami`"
    decorators = []

    def handle_imp(self, **kwargs):  # noqa
        me = whoami()[:-1]
        src_dir = self.get_config("/ROOT/src_dir")
        self.runcmd(
            [
                "sudo",
                "chown",
                "-R",
                "%s:%s" % (me, me),
                os.path.basename(src_dir)
            ],
            cwd=os.path.dirname(src_dir)
        )
