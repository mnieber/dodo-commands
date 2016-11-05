"""Installs dodo commands in the folder that contains install.py."""
import argparse
from six.moves import configparser
import os
import sys
from plumbum.cmd import chmod


def create_config(install_folder, projects_dir):
    """Write global dodo commands configuration."""
    config = configparser.ConfigParser()
    config.add_section("DodoCommands")

    config.set(
        "DodoCommands",
        "projects_folder",
        os.path.expanduser(projects_dir)
    )
    config.set(
        "DodoCommands",
        "diff_tool",
        "diff"
    )
    with open(
        os.path.join(
            install_folder, "dodo_commands.config"
        ),
        "w"
    ) as config_file:
        config.write(config_file)


def create_activate_script(bin_folder):
    """Write a version of dodo-activate with the correct shebang."""
    script_filename = os.path.join(bin_folder, "dodo-activate")
    with open(script_filename, "w") as f:
        f.write("#!" + sys.executable + "\n")
        f.write("from dodo_activate import Activator\n")
        f.write("Activator().run()\n")
    chmod("+x", script_filename)


def create_install_defaults_script(bin_folder):
    """Write a version of dodo-install-defaults with the correct shebang."""
    script_filename = os.path.join(bin_folder, "dodo-install-defaults")
    with open(script_filename, "w") as f:
        f.write("#!" + sys.executable + "\n")
        f.write("from dodo_install_defaults import DefaultsInstaller\n")
        f.write("DefaultsInstaller().run()\n")
    chmod("+x", script_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--projects_dir', default="~/projects")
    args = parser.parse_args()

    bin_folder = os.path.dirname(__file__)
    source_folder = os.path.dirname(bin_folder)

    create_config(source_folder, args.projects_dir)
    create_activate_script(bin_folder)
    create_install_defaults_script(bin_folder)
    print (
        "Finished configuring.\n"
        "Call the following command to extend the PATH for "
        "finding the dodo-activate command:\n"
        "echo 'export PATH=$PATH:%s' >> ~/.bashrc"
        % os.path.abspath(bin_folder)
    )
