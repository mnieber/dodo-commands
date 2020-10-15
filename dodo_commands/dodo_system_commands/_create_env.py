import os

from dodo_commands.framework.paths import Paths

from ._create_config_dir import create_config_dir
from ._create_dodo_script import create_dodo_script
from ._create_env_dir import create_env_dir
from ._create_python_env import create_python_env


def _python_env_filename(python_env_dir, basename):
    return os.path.join(python_env_dir, "bin", basename)


def _remove_dir(x):
    if os.path.exists(x):
        print("Clean-up step: rm -rf %s" % x)


def _remove_file(x):
    if os.path.exists(x):
        print("Clean-up step: rm %s" % x)


def register_env(env, project_dir, config_dir, python_env_dir, undo_steps):
    global_bin_dir = os.path.join(Paths().global_config_dir(), "bin")
    named_dodo_filename = os.path.join(global_bin_dir, "dodo-%s" % env)
    env_dir = Paths().env_dir(env)
    python_path = (
        _python_env_filename(python_env_dir, "python") if python_env_dir else None
    )

    if not os.path.exists(global_bin_dir):
        os.makedirs(global_bin_dir)

    if not os.path.exists(project_dir):
        undo_steps.append(lambda: _remove_dir(project_dir))
        os.makedirs(project_dir)

    if not os.path.exists(config_dir):
        undo_steps.append(lambda: _remove_dir(config_dir))
        create_config_dir(config_dir)

    if not os.path.exists(named_dodo_filename):
        undo_steps.append(lambda: _remove_file(named_dodo_filename))
        create_dodo_script(env, named_dodo_filename, python_path)

    undo_steps.append(lambda: _remove_dir(env_dir))
    create_env_dir(env, env_dir, project_dir, config_dir, python_env_dir)


def forget_env(env):
    global_bin_dir = os.path.join(Paths().global_config_dir(), "bin")
    named_dodo_filename = os.path.join(global_bin_dir, "dodo-%s" % env)

    env_dir = Paths().env_dir(env)

    python_env_dir = os.path.join(env_dir, "python_env_dir")
    if os.path.exists(python_env_dir):
        python_env_dir = os.path.realpath(python_env_dir)
        dodo_filename = _python_env_filename(python_env_dir, "dodo")
        _remove_file(dodo_filename)

    _remove_file(named_dodo_filename)
    _remove_dir(env_dir)


def register_python_env(python, env, python_env_dir, undo_steps):
    dodo_filename = _python_env_filename(python_env_dir, "dodo")
    python_path = _python_env_filename(python_env_dir, "python")

    if not os.path.exists(python_env_dir):
        undo_steps.append(lambda: _remove_dir(python_env_dir))
        create_python_env(python, python_env_dir, env)

    if not os.path.exists(dodo_filename):
        undo_steps.append(lambda: _remove_file(dodo_filename))
        create_dodo_script(None, dodo_filename, python_path)
