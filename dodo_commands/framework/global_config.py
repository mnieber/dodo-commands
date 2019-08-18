import os

from six.moves import configparser

from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import symlink


def load_global_config_parser():
    config_parser = configparser.ConfigParser()
    config_parser.read(Paths().global_config_filename())
    return config_parser


def write_global_config_parser(config_parser):
    """Save configuration."""
    with open(Paths().global_config_filename(), "w") as f:
        config_parser.write(f)


def projects_dir():
    return os.path.expanduser(load_global_config_parser().get(
        "settings", "projects_dir"))


_global_config = """[settings]
projects_dir=~/projects
python_interpreter=python
diff_tool=diff

[recent]
"""


def _touch_init_py(dir_name):
    init_py = os.path.join(dir_name, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, 'w'):
            pass


def create_global_config():
    """Create config file and default_commands dir."""
    base_dir = Paths().global_config_dir()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    config_filename = Paths().global_config_filename()
    if not os.path.exists(config_filename):
        with open(config_filename, 'w') as f:
            f.write(_global_config)

    default_commands_dir = Paths().default_commands_dir()
    if not os.path.exists(default_commands_dir):
        os.mkdir(default_commands_dir)
        _touch_init_py(default_commands_dir)
        symlink(
            os.path.join(Paths().extra_dir(), "dodo_standard_commands"),
            os.path.join(Paths().default_commands_dir(),
                         "dodo_standard_commands"))

    global_commands_dir = Paths().global_commands_dir()
    if not os.path.exists(global_commands_dir):
        os.mkdir(global_commands_dir)
        _touch_init_py(global_commands_dir)
