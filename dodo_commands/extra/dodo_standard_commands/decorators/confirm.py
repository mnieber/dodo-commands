import os
import sys

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.util import query_yes_no

local = plumbum.local


def _count_confirm_in_argv():
    result = 0
    for arg in sys.argv:
        if arg == "--confirm":
            result += 1
        if arg.startswith("-") and not arg.startswith("--"):
            result += arg.count("c")
        if arg == "--":
            break
    return result


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
        or _count_confirm_in_argv()
        or os.environ.get("__DODO_UNIVERSAL_CONFIRM__", None) == "1"
    )


def _is_echo(command_line_args):
    return getattr(command_line_args, "echo", False)


class Decorator:  # noqa
    def is_used(self, config, command_name, decorator_name):
        return True

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
            action="store_true",
            help="Print all commands instead of running them",
        )

    def modify_args(self, command_line_args, args_tree_root_node, cwd):  # noqa
        if _count_confirm_in_argv() > 1:
            local.env["__DODO_UNIVERSAL_CONFIRM__"] = "1"

        if _is_echo(command_line_args) and not Dodo.safe:
            raise CommandError(
                "The --echo option is not supported for unsafe commands.\n"
                + "Since this command is marked as unsafe, some operations will "
                + "be performed directly, instead of echoed to the console. "
                + "Use --confirm if you wish to execute with visual feedback. "
            )

        if _is_confirm(command_line_args) and not Dodo.safe:
            if not query_yes_no(
                "Since this command is marked as unsafe, some operations will "
                + "be performed without asking for confirmation. Continue?",
                default="no",
            ):
                sys.exit(1)

        if not _ask_confirmation(
            args_tree_root_node,
            cwd or local.cwd,
            _is_echo(command_line_args),
            _is_confirm(command_line_args),
        ):
            return None, None

        return args_tree_root_node, cwd
