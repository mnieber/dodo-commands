# SHEBANG_PLACEHOLDER_PLEASE_DONT_MODIFY_THIS_LINE

import os
import sys

if __name__ == "__main__":
    if not os.path.dirname(os.path.abspath(__file__)).endswith("env/bin"):
        print (
            'Error: this script must be run from the env/bin folder'
        )
        sys.exit(1)

    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.append(project_dir)
    from dodo_commands.framework import execute_from_command_line
    execute_from_command_line(sys.argv)
