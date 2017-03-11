import os
import sys
from dodo_commands.framework import execute_from_command_line


def main():  # noqa
    os.environ["DODO_COMMANDS_PROJECT_DIR"] = ""
    execute_from_command_line(sys.argv)
