from dodo_commands.framework.util import make_executable


def create_dodo_script(env, dodo_file, python_path):
    with open(dodo_file, "w") as ofs:

        def add(x):
            ofs.write((x + "\n").format(python_path=python_path, env=env))

        if python_path:
            add("#!{python_path}")
        else:
            add("#!/usr/bin/env python")

        add("import os")
        add("import sys")
        add("")
        add("from dodo_commands.framework import execute_from_command_line")
        add("")
        add('if __name__ == "__main__":')
        if env:
            add('    os.environ["DODO_COMMANDS_ENV"] = "{env}"')
        add("    execute_from_command_line(sys.argv)")
    make_executable(dodo_file)
