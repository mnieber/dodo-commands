"""Installs dodo commands in the dir that contains install.py."""
import argparse
from six.moves import configparser
import os


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
    print(
        "Finished configuring.\n"
        "Call the following command to extend the PATH for "
        "finding the dodo-activate command:\n"
        "echo 'export PATH=$PATH:%s' >> ~/.bashrc"
        % os.path.abspath(bin_dir)
    )
