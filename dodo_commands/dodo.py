import sys
from dodo_commands.framework import execute_from_command_line
from dodo_commands.framework.config import create_global_config


def main():  # noqa
    create_global_config()
    execute_from_command_line(sys.argv)
