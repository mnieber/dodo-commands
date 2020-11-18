import os
import shutil
import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install


class InstallPrivatePackages(install):
    def _package_dirname(self):
        return os.path.join(
            self.install_lib, "dodo_commands", "dependencies", "packages"
        )

    def _bin_dirname(self):
        return os.path.join(self.install_lib, "dodo_commands", "bin")

    def _install_packages(self, package_dirname):
        if not os.path.exists(package_dirname):
            os.makedirs(package_dirname)

        for dependency in [
            "python-dotenv==0.12.0",
            "plumbum==1.6.8",
            "ruamel.yaml==0.16.10",
            "parsimonious==0.8.1",
            "six==1.14.0",
            "funcy==1.14",
            "ansimarkup==1.4.0",
            "argcomplete==1.11.1",
            "semantic_version==2.8.4",
        ]:
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
            except:  # noqa
                pass

    def _install_autocomplete_scripts(self, bin_dirname):
        bash_autocomplete_dir = "/etc/bash_completion.d/"
        fish_autocomplete_dir = "/etc/fish/conf.d/"

        for (f, d) in (
            ("dodo_autocomplete.sh", bash_autocomplete_dir),
            ("dodo_autocomplete.fish", fish_autocomplete_dir),
        ):
            try:
                if not os.path.exists(d):
                    os.makedirs(d)
                shutil.copy(os.path.join(bin_dirname, f), d)
            except:  # noqa
                pass

    def run(self):
        super(InstallPrivatePackages, self).run()
        self._install_packages(self._package_dirname())
        self._install_autocomplete_scripts(self._bin_dirname())


setup(
    name="dodo_commands",
    version="0.36.0",
    description="Project-aware development environments, inspired by django-manage",
    url="https://github.com/mnieber/dodo_commands",
    download_url="https://github.com/mnieber/dodo_commands/tarball/0.36.0",
    author="Maarten Nieber",
    author_email="hallomaarten@yahoo.com",
    license="MIT",
    packages=find_packages(),
    package_data={
        "dodo_commands": [
            "bin/*.sh",
            "bin/*.fish",
            "extra/dodo_standard_commands/*.meta",
            "extra/dodo_docker_commands/*.meta",
            "extra/fish/functions/*.fish",
            "extra/fish/conf.d/*.fish",
        ]
    },
    entry_points={
        "console_scripts": [
            "dodo=dodo_commands.dodo:main",
        ]
    },
    data_files=[
        (
            "/etc/bash_completion.d",
            [
                "dodo_commands/bin/dodo_autocomplete.sh",
                "dodo_commands/bin/sdodo_autocomplete.sh",
            ],
        ),
        ("/etc/fish/conf.d", ["dodo_commands/bin/dodo_autocomplete.fish"]),
    ],
    cmdclass={"install": InstallPrivatePackages},
    install_requires=[],
    zip_safe=False,
)
