from setuptools import setup


setup(name='dodo_commands',
      version='0.9.1',
      description='Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.9.1',
      author='Maarten Nieber',
      author_email='hallomaarten@yahoo.com',
      license='MIT',
      packages=[
          'dodo_commands',
          'dodo_commands.framework',
          'dodo_commands.system_commands',
      ],
      package_data={
          'dodo_commands': [
              'extra/__init__.py',
              'extra/git_commands/*.py',
              'extra/git_commands/*.meta',
              'extra/standard_commands/*.py',
              'extra/standard_commands/*.meta',
              'extra/standard_commands/decorators/*.py',
              'extra/webdev_commands/*.py',
              'extra/webdev_commands/*.meta',
          ]
      },
      entry_points={
          'console_scripts': [
              'dodo=dodo_commands.dodo:main',
          ]
      },
      install_requires=[
          'argcomplete',
          'plumbum',
          'ruamel.yaml',
          'six',
      ],
      zip_safe=False)
