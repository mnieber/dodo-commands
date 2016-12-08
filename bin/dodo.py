# SHEBANG_PLACEHOLDER_PLEASE_DONT_MODIFY_THIS_LINE

from os.path import dirname, abspath
import sys

if __name__ == "__main__":
    if not dirname(abspath(__file__)).endswith("env/bin"):
        sys.stderr.write(
            'Error: this script must be run from the env/bin directory'
        )
        sys.exit(1)

    project_dir = abspath(dirname(dirname(dirname(dirname(__file__)))))
    sys.path.append(project_dir)

    from dodo_commands.framework import execute_from_command_line
    execute_from_command_line(sys.argv)
