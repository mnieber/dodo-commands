"""Creates a git tag and allows to interactively rebase onto that tag."""
from __future__ import absolute_import
from dodo_commands.extra.standard_commands import (
    DodoCommand, CommandError
)
from git import Repo


class Command(DodoCommand):  # noqa
    @staticmethod
    def _split_for(x):
        return x + "_split"

    def add_arguments_imp(self, parser):  # noqa
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--move', dest='move_split_to', action='store',
            help='Move the split point'
        )
        group.add_argument(
            '--rebase', dest='onto', action='store',
            help='Rebase current feature onto origin/onto'
        )
        group.add_argument(
            '--ri', dest='rebase_interactive', action='store_true',
            help='Interactively rebase current feature onto split point'
        )

    def handle_imp(self, move_split_to, onto, rebase_interactive, **kwargs):  # noqa
        repo = Repo(".")
        branch = repo.head.ref.name

        if onto:
            try:
                result = repo.git.rebase(
                    self._split_for(branch),
                    onto=onto,
                    with_extended_output=True
                )
                if result[0] == 0:
                    repo.create_tag(
                        self._split_for(branch),
                        ref=onto,
                        force=True
                    )
            except Exception as e:
                raise CommandError(str(e))

        if move_split_to:
            repo.create_tag(
                self._split_for(branch),
                ref=move_split_to,
                force=True
            )

        if rebase_interactive:
            print("git rebase --interactive -- %s_split" % branch)
