import os
import sys

from dodo_commands.framework.command_error import CommandError  # noqa
from dodo_commands.framework.command_map import execute_script
from dodo_commands.framework.singleton import Dodo  # noqa
from dodo_commands.framework.version import get_version


def _handle_exception(e):
    if "_ARGCOMPLETE" in os.environ:
        sys.exit(0)

    if "--traceback" in sys.argv or not isinstance(e, CommandError):
        raise
    sys.stderr.write("%s: %s\n" % (e.__class__.__name__, e))
    sys.exit(1)


def execute_from_command_line(argv):
    os.environ["__DODO__"] = "1"

    if "_ARGCOMPLETE" in os.environ:
        sys.argv += os.environ["COMP_LINE"].split()[1:2]

    try:
        ctr = Dodo.get_container()

        # TODO: move to action_execute_command
        if ctr.command_line.command_name == "--version":
            print(get_version())
            sys.exit(0)

        if ctr.command_line.is_trace:
            sys.stderr.write("%s\n" % ctr.command_line.get_trace())
            sys.exit(0)

        if ctr.command_line.command_name not in ctr.commands.command_map:
            raise CommandError(
                "Unknown dodo command: %s" % ctr.command_line.command_name
            )

        execute_script(ctr.commands.command_map, ctr.command_line.command_name)
    except KeyboardInterrupt:
        print("\n")
        sys.exit(1)
    except Exception as e:
        _handle_exception(e)
