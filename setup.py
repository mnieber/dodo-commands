import os
import subprocess
import sys
from distutils.command.install_data import install_data

from setuptools import setup


class InstallPrivatePackages(install_data):
    def _packages_dirname(self):
        import dodo_commands
        dirname = os.path.dirname(os.path.realpath(dodo_commands.__file__))
        return os.path.join(dirname, *("dependencies.packages".split(".")))

    def _install_packages(self, packages_dirname):
        for dependency in [
                'plumbum',
                'ruamel.yaml',
                'parsimonious',
                'six',
                'funcy',
                'ansimarkup',
                'argcomplete',
                'semantic_version',
        ]:
            package_dirname = os.path.join(packages_dirname,
                                           *dependency.split("."))
            module_filename = package_dirname + ".py"
            if not os.path.exists(package_dirname) and not os.path.exists(
                    module_filename):
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--target',
                    packages_dirname, dependency
                ])

    def run(self):
        super().run()
        self._install_packages(self.packages_dirname())


setup(name='dodo_commands',
      version='0.29.1',
      description=
      'Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.29.1',
      author='Maarten Nieber',
      author_email='hallomaarten@yahoo.com',
      license='MIT',
      packages=[
          'dodo_commands',
          'dodo_commands.framework',
          'dodo_commands.dodo_system_commands',
      ],
      package_data={
          'dodo_commands': [
              'extra/__init__.py',
              'extra/dodo_standard_commands/*.py',
              'extra/dodo_standard_commands/*.meta',
              'extra/dodo_standard_commands/decorators/*.py',
          ]
      },
      entry_points={'console_scripts': [
          'dodo=dodo_commands.dodo:main',
      ]},
      cmdclass={'install_data': InstallPrivatePackages},
      install_requires=[],
      zip_safe=False)
