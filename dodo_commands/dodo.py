import os
import sys
from dodo_commands.framework import execute_from_command_line
from dodo_commands.framework.util import create_global_config


def main():  # noqa
    create_global_config()
    os.environ["DODO_COMMANDS_PROJECT_DIR"] = ""
    execute_from_command_line(sys.argv)
