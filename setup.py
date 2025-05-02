import os
import site
import subprocess
import sys

from setuptools import setup


def install_packages():
    """Install private packages to the correct directory."""
    # Find the site-packages directory
    site_packages = site.getsitepackages()[0]
    package_dirname = os.path.join(
        site_packages, "dodo_commands", "dependencies", "packages"
    )

    # Create the directory if it doesn't exist
    if not os.path.exists(package_dirname):
        os.makedirs(package_dirname, exist_ok=True)

    print(f"Installing private packages to {package_dirname}")

    dependencies = [
        "python-dotenv==0.12.0",
        "plumbum==1.6.8",
        "ruamel.yaml==0.16.10",
        "parsimonious==0.8.1",
        "six==1.14.0",
        "funcy==1.14",
        "ansimarkup==1.4.0",
        "argcomplete==1.11.1",
        "semantic_version==2.8.4",
    ]

    for dependency in dependencies:
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    package_dirname,
                    dependency,
                ]
            )
            print(f"Installed {dependency}")
        except Exception as e:
            print(f"Failed to install {dependency}: {e}")


def _is_installing():
    # More accurately check if this is an actual install command
    install_commands = {"install", "develop"}

    # Check for pip install scenarios
    is_pip_install = False
    if "egg_info" in sys.argv:
        # pip install will run egg_info, but we need additional checks
        # pip install -e . will typically have 'develop' in sys.argv
        # pip install . will have 'install' in sys.argv later
        # For safety, we can check if the environment suggests pip is running
        is_pip_install = (
            "PIP_PYTHON_PATH" in os.environ
            or os.environ.get("PYTHONPATH", "").find("pip") >= 0
        )

    # True installation occurs only for specific commands
    is_installing = any(cmd in sys.argv for cmd in install_commands) or is_pip_install
    return is_installing


if __name__ == "__main__":
    setup(
        data_files=[
            (
                "/etc/bash_completion.d",
                [
                    "dodo_commands/bin/dodo_autocomplete.sh",
                ],
            ),
            ("/etc/fish/conf.d", ["dodo_commands/bin/dodo_autocomplete.fish"]),
        ],
    )

    # Run the install_packages function after setup
    if _is_installing():
        install_packages()
