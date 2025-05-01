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
    install_packages()
