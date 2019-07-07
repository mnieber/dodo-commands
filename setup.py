from setuptools import setup

setup(name='dodo_commands',
      version='0.26.0',
      description=
      'Project-aware development environments, inspired by django-manage',
      url='https://github.com/mnieber/dodo_commands',
      download_url='https://github.com/mnieber/dodo_commands/tarball/0.26.0',
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
      install_requires=[
          'argcomplete',
          'plumbum',
          'python-dotenv',
          'ruamel.yaml',
          'six',
      ],
      zip_safe=False)
