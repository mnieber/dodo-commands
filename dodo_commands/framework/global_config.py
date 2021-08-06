import os

from dodo_commands.dependencies.get import six
from dodo_commands.dodo_system_commands._create_env_dir import create_env_dir
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import symlink

configparser = six.moves.configparser


def global_config_get(config, section, key, default=""):
    if config is None:
        config = load_global_config_parser()
    return config.get(section, key) if config.has_option(section, key) else default


def load_global_config_parser():
    config_parser = configparser.ConfigParser()
    config_parser.read(Paths().global_config_filename())
    return config_parser


def write_global_config_parser(config_parser):
    """Save configuration."""
    with open(Paths().global_config_filename(), "w") as f:
        config_parser.write(f)


def projects_dir():
    return os.path.expanduser(
        load_global_config_parser().get("settings", "projects_dir")
    )


_global_config = """[settings]
projects_dir=~/projects
python_interpreter=python
diff_tool=diff

[recent]
"""

_default_project_config = """ROOT:
  version: 1.0.0
  command_path:
  - ${/ROOT/project_dir}/commands/*
"""

_default_config_mixin = """ROOT:
  src_dir: ${/ROOT/project_dir}/src

DIAL:
  default:
    '1': dodo
  ctrl:
    '1': ${/ROOT/project_dir}/
    '2': ~/
  shift:
    '1': ${/ROOT/src_dir}/
"""


def _touch_init_py(dir_name):
    init_py = os.path.join(dir_name, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, "w"):
            pass


def create_global_config():
    """Create config file and default_commands dir."""
    base_dir = Paths().global_config_dir()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    config_filename = Paths().global_config_filename()
    if not os.path.exists(config_filename):
        with open(config_filename, "w") as f:
            f.write(_global_config)

    default_config_mixin_filename = Paths().default_config_mixin_filename()
    if not os.path.exists(default_config_mixin_filename):
        with open(default_config_mixin_filename, "w") as f:
            f.write(_default_config_mixin)

    default_project_dir = Paths().default_project_dir()

    if not os.path.exists(default_project_dir):
        os.makedirs(default_project_dir)
        default_project_config_fn = os.path.join(default_project_dir, "config.yaml")
        with open(default_project_config_fn, "w") as f:
            f.write(_default_project_config)

    default_env_dir = Paths().env_dir("default")
    if not os.path.exists(default_env_dir):
        create_env_dir(
            "default", default_env_dir, default_project_dir, default_project_dir, None
        )

    preset_commands_dirs = ("dodo_standard_commands", "dodo_docker_commands")
    global_commands_dir = Paths().global_commands_dir()
    if not os.path.exists(global_commands_dir):
        os.mkdir(global_commands_dir)
        _touch_init_py(global_commands_dir)
        for d in preset_commands_dirs:
            symlink(
                os.path.join(Paths().extra_dir(), d),
                os.path.join(global_commands_dir, d),
            )

    default_commands_dir = Paths().default_commands_dir()
    if not os.path.exists(default_commands_dir):
        os.makedirs(default_commands_dir)
        _touch_init_py(default_commands_dir)
        for d in preset_commands_dirs:
            symlink(
                os.path.join(global_commands_dir, d),
                os.path.join(default_commands_dir, d),
            )
