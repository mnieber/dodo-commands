import os

import dodo_commands
from dodo_commands import CommandError
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.util import symlink


def site_packages_dir(python_env_dir):
    python = plumbum.local[os.path.join(python_env_dir, "bin", "python")]

    result = python(
        "-c",
        "from distutils.sysconfig import get_python_lib; " + "print(get_python_lib())",
    )
    while result[-1] in ["\n", "\r"]:
        result = result[:-1]
    return result


def create_python_env(python, python_env_dir, env):
    try:
        plumbum.local["virtualenv"]("--version")
    except:  # noqa
        raise CommandError("Could not find virtualenv, please install it first.")

    plumbum.local["virtualenv"]("-p", python, python_env_dir, "--prompt", env)

    symlink(
        os.path.realpath(os.path.dirname(dodo_commands.__file__)),
        os.path.join(site_packages_dir(python_env_dir), "dodo_commands"),
    )
