import atexit
import os
import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install


class InstallPrivatePackages(install):
    def run(self):
        def _post_install():
            def find_module_path():
                for p in sys.path:
                    if os.path.isdir(p) and "dodo_commands" in os.listdir(p):
                        return os.path.join(p, "dodo_commands")

            install_path = find_module_path()

            # Add your post install code here
            packages_dirname = os.path.join(install_path, "dependencies",
                                            "packages")
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
                    print("Install %s in %s" % (dependency, packages_dirname))
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', '--target',
                        packages_dirname, dependency
                    ])
                except:  # noqa
                    pass

        atexit.register(_post_install)
        super().run()


setup(name='dodo_commands',
      version='0.30.5',
      description=
      'Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.30.5',
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
      cmdclass={'install': InstallPrivatePackages},
      install_requires=[],
      zip_safe=False)
