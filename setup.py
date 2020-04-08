import os
import subprocess
import sys
from distutils.command.install_data import install_data

from setuptools import find_packages, setup


class InstallPrivatePackages(install_data):
    def _packages_dirname(self):
        def find_module_path():
            for p in sys.path:
                if os.path.isdir(p) and "dodo_commands" in os.listdir(p):
                    return os.path.join(p, "dodo_commands")

        install_path = find_module_path()
        return os.path.join(install_path, "dependencies", "packages")

    def _install_packages(self, packages_dirname):
        if not os.path.exists(packages_dirname):
            os.makedirs(packages_dirname)

        for dependency in [
                'python-dotenv==0.12.0',
                'plumbum==1.6.8',
                'ruamel.yaml==0.16.10',
                'parsimonious==0.8.1',
                'six==1.14.0',
                'funcy==1.14',
                'ansimarkup==1.4.0',
                'argcomplete==1.11.1',
                'semantic_version==2.8.4',
        ]:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--target',
                    packages_dirname, dependency
                ])
            except:  # noqa
                pass

    def run(self):
        super().run()
        self._install_packages(self._packages_dirname())


setup(name='dodo_commands',
      version='0.30.3',
      description=
      'Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.30.3',
      author='Maarten Nieber',
      author_email='hallomaarten@yahoo.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'dodo_commands': [
              'extra/dodo_standard_commands/*.meta',
              'extra/dodo_docker_commands/*.meta',
          ]
      },
      entry_points={'console_scripts': [
          'dodo=dodo_commands.dodo:main',
      ]},
      data_files=[('/etc/bash_completion.d', [
          'dodo_commands/bin/dodo_autocomplete.sh',
          'dodo_commands/bin/sdodo_autocomplete.sh'
      ]), ('/etc/fish/conf.d', ['dodo_commands/bin/dodo_autocomplete.fish'])],
      cmdclass={'install_data': InstallPrivatePackages},
      install_requires=[],
      zip_safe=False)
