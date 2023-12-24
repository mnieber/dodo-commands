import os
import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.util import query_yes_no

local = plumbum.local


def _ask_confirmation(args, cwd, is_echo, is_confirm):
    """Ask the user whether to continue with executing func."""

    def to_str():
        return args.to_str(slash=args.children)

    if is_echo:
        print(to_str())
        return False

    if is_confirm:
        print("(%s) %s" % (cwd, to_str()))
        if not query_yes_no("confirm?"):
            return False
        else:
            print("")

    return True


def _is_echo(command_line_args):
    return getattr(command_line_args, "echo", False)


def _is_confirm(command_line_args):
    return (
        getattr(command_line_args, "confirm", False)
        or os.environ.get("__DODO_UNIVERSAL_CONFIRM__", None) == "1"
    )


def _is_echo(command_line_args):
    return getattr(command_line_args, "echo", False)


class Decorator:  # noqa
    def add_arguments(self, parser):  # noqa
        parser.add_argument(
            "-c",
            "--confirm",
            action="count",
            help="Confirm each performed action before its execution."
            + " Use twice (e.g. dodo foo -cc) to indicate that also nested calls must be confirmed.",
        )

        parser.add_argument(
            "-e",
            "--echo",
            action="count",
            help="Print all commands instead of running them",
        )

    def install(self):
        parser = ArgumentParser(add_help=False)
        self.add_arguments(parser)
        known_args, args = parser.parse_known_args()

        if known_args.confirm and known_args.confirm > 1:
            local.env["__DODO_UNIVERSAL_CONFIRM__"] = "1"

        if known_args.echo and not Dodo.safe:
            raise CommandError(
                "The --echo option is not supported for unsafe commands.\n"
                + "Since this command is marked as unsafe, some operations will "
                + "be performed directly, instead of echoed to the console. "
                + "Use --confirm if you wish to execute with visual feedback. "
            )

        if known_args.confirm and not Dodo.safe:
            if not query_yes_no(
                "Since this command is marked as unsafe, some operations will "
                + "be performed without asking for confirmation. Continue?",
                default="no",
            ):
                sys.exit(1)

    def modify_args(self, command_line_args, args_tree_root_node, cwd):  # noqa
        if not _ask_confirmation(
            args_tree_root_node,
            cwd or local.cwd,
            _is_echo(command_line_args),
            _is_confirm(command_line_args),
        ):
            return None, None

        return args_tree_root_node, cwd
