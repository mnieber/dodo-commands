# Version history

## 0.4.1

- Also use DOCKER/volumes_from_list in docker decorator
- Use standard docker container names in webpack, autoless and pytest

## 0.4.0

- Commands can use decorated.docker_options to add more docker options
- Remove port argument from docker decorator
- Link pg docker container in django-manage command

## 0.3.10

- Require option --force or --confirm in bootstrap command
- Add pytest_args argument to pytest command

## 0.3.9

- Fix: broken paths

## 0.3.8

- Fix: avoid permission problems by not installing config file during setup
- Add option --latest to dodo-activate

## 0.3.7

- Fix problem with dodo diff <somefile>
- Change --command option in "docker" to a positional argument

## 0.3.6

- Remove git-gui command (use dodo git gui instead)
- Simplify the cd and which commands
- Print an error if config layer filename not found

## 0.3.5

- Update documentation

## 0.3.4

- Fix PyPI installation problem

## 0.3.3

- Fix: ensure less output directory exists in autoless command
- Make the git command generic

## 0.3.1

- Fix: resolve references in command_path

## 0.3.0

- BREAKING: symlink dodo_commands in the site-packages of the dodo project
- BREAKING: remove framework and default_commands dirs from dodo project dir

## 0.2.3

- Simplify django-manage command and make it work for Python 2

## 0.2.2

- Add argument --port to docker decorator

## 0.2.1

- Fix: Don't crash on non-standard filenames in /ROOT/layers
- Add optional argument --command to "dodo docker"
- Add argument --res to cd and which commands

## 0.2.0

- BREAKING: Use pip to install dodo_commands
- BREAKING: Many small changes in api

## 0.1.6

- FIX: Remove stray pudb invocation in bootstrap command
- Small improvements in commands: django-manage, autoless
- Also disable docker if /DOCKER/enabled equals "False"

## 0.1.5

- New command chown-src
- Better error reporting in gitsplit command
- Configurable python interpreter in django-manage command
- Make directories in ${DOCKER/extra_dirs} available in dockerbuild command
- Use ${/DOCKER/default_cwd} in docker command
- Add argument 'branch' to bootstrap command

## 0.1.4

- Allow to create a project in an existing directory if no dodo_commands directory exists

## 0.1.3

- FIX: Allow storing CommandPaths in configuration layers.
- FIX: Use symlink dodo_commands/defaults/project in diff command

## 0.1.2

- BREAKING: Store env inside dodo_commands, and config.yaml in dodo_commands/res
- FIX: Fix layer and print-config, update README.md to explain configuration layers

## 0.1.1

- FIX: Added documentation and fixed broken references to defaults/commands
- NEW: Argument --create-from to dodo_activate

## 0.1.0

- BREAKING: Renamed option projects_folder to projects_dir in dodo_commands.config.
- BREAKING: Added option python_interpreter (default=python) to dodo_commands.config. This option sets the python interpreter that is used in the project's virtualenv.
- FIX: Changed version back from 1.0.0 to 0.1.0 to indicate beta status
- FIX: Several other fixes
- NEW: Commands new-command, git-gui, gitk, gitsplit, git, config-get, bootstrap
