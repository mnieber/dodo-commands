import os

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import symlink


def env_var_template(env):
    return "export DODO_COMMANDS_ENV={env}\n".format(env=env)


def deactivate_template_bash():
    return """if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual env: $VIRTUAL_ENV"
    deactivate
fi
"""


def deactivate_template_fish():
    return """if test -n "$VIRTUAL_ENV"
    echo "Deactivating virtual env: $VIRTUAL_ENV"
    deactivate
end
"""


def source_startup_files_fish(config_dir):
    return """for file in {config_dir}/.dodo-start-env/*
    source $file
end
""".format(
        config_dir=config_dir
    )


def activate_template(envs_dir, activate):
    return """source {envs_dir}/$DODO_COMMANDS_ENV/python_env_dir/bin/{activate}
""".format(
        envs_dir=envs_dir, activate=activate
    )


def create_env_dir(env, env_dir, project_dir, config_dir, python_env_dir):
    if os.path.exists(env_dir):
        raise CommandError("Environment dir already exists: %s" % env_dir)

    os.makedirs(env_dir)
    symlink(project_dir, os.path.join(env_dir, "project_dir"))
    symlink(config_dir, os.path.join(env_dir, "config_dir"))

    if python_env_dir:
        symlink(python_env_dir, os.path.join(env_dir, "python_env_dir"))

    with open(os.path.join(env_dir, "activate.bash"), "w") as ofs:
        ofs.write(env_var_template(env))
        ofs.write(deactivate_template_bash())
        if python_env_dir:
            ofs.write(activate_template(Paths().envs_dir(), "activate"))

    with open(os.path.join(env_dir, "activate.fish"), "w") as ofs:
        ofs.write(env_var_template(env))
        ofs.write(deactivate_template_fish())
        ofs.write(source_startup_files_fish(config_dir))
        if python_env_dir:
            ofs.write(activate_template(Paths().envs_dir(), "activate.fish"))
