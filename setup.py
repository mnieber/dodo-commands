from setuptools import find_packages, setup

setup(name='dodo_commands',
      version='0.30.1',
      description=
      'Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.30.1',
      author='Maarten Nieber',
      author_email='hallomaarten@yahoo.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'dodo_commands': [
              'bin/*.fish',
              'bin/*.sh',
              'extra/dodo_standard_commands/*.meta',
              'extra/dodo_docker_commands/*.meta',
          ]
      },
      entry_points={'console_scripts': [
          'dodo=dodo_commands.dodo:main',
      ]},
      install_requires=[],
      zip_safe=False)
