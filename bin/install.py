"""Installs dodo commands in the dir that contains install.py."""
import argparse
from six.moves import configparser
import os
import sys
from plumbum.cmd import chmod


def create_config(install_dir, projects_dir, python_interpreter):
    """Write global dodo commands configuration."""
    config = configparser.ConfigParser()
    config.add_section("DodoCommands")

    config.set(
        "DodoCommands",
        "projects_dir",
        os.path.expanduser(projects_dir)
    )
    config.set(
        "DodoCommands",
        "python_interpreter",
        python_interpreter
    )
    config.set(
        "DodoCommands",
        "diff_tool",
        "diff"
    )
    with open(
        os.path.join(
            install_dir, "dodo_commands.config"
        ),
        "w"
    ) as config_file:
        config.write(config_file)

def make_executable(script_filename):
    """Do chmod +x script_filename."""
    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | 0o111)


def create_activate_script(bin_dir):
    """Write a version of dodo-activate with the correct shebang."""
    script_filename = os.path.join(bin_dir, "dodo-activate")
    with open(script_filename, "w") as f:
        f.write("#!" + sys.executable + "\n")
        f.write("from dodo_activate import Activator\n")
        f.write("Activator().run()\n")
    make_executable(script_filename)


def create_install_defaults_script(bin_dir):
    """Write a version of dodo-install-defaults with the correct shebang."""
    script_filename = os.path.join(bin_dir, "dodo-install-defaults")
    with open(script_filename, "w") as f:
        f.write("#!" + sys.executable + "\n")
        f.write("from dodo_install_defaults import DefaultsInstaller\n")
        f.write("DefaultsInstaller().run()\n")
    make_executable(script_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--projects_dir',
        default="~/projects",
        help="Location where your projects are stored."
    )
    parser.add_argument(
        '--python',
        default="python",
        dest="python_interpreter",
        help=(
            "Python interpreter that is used in the virtual env " +
            "of your projects."
        )
    )
    args = parser.parse_args()

    bin_dir = os.path.dirname(__file__)
    source_dir = os.path.dirname(bin_dir)

    create_config(source_dir, args.projects_dir, args.python_interpreter)
    create_activate_script(bin_dir)
    create_install_defaults_script(bin_dir)
    print(
        "Finished configuring.\n"
        "Call the following command to extend the PATH for "
        "finding the dodo-activate command:\n"
        "echo 'export PATH=$PATH:%s' >> ~/.bashrc"
        % os.path.abspath(bin_dir)
    )
