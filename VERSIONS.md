# Version history

## 0.38.0

- Fix: call to dodo which --config
- Improve documentation for installing the "dodo dial" key-bindings

## 0.37.0

- Fix: remove references to sdodo
- Restore functionality where `dodo which src` prints src_dir location
- Improve message about initializing a dodo commands project directory
- Improve the documentation of the Dodo Commands goals
- Add dodo browse command
- Fix: --help did not correctly show the name of the dodo command

## 0.36.0

- Add extra fish files
- Fix: parsing of --help
- Fix: broken autocomplete

## 0.35.0

- Add --yaml argument to new-command script
- Fix optional args in yaml_command_handler
- Fix new-command script
- Refactor to use register and run(ctr, action)
- Add new exec command and kubectl command
- Reuse existing tmux session in dodo menu --tmux
- Treat second occurrence of -- as the start of more dodo arguments
- Allow expanded expression in ConfigArg
- Add --list argument to dodo dial
- Merge dodo cd into dodo which

## 0.34.0

- Add command docker-restart
- Fix: not all aliases were proposed in expand action
- Fix docker-exec when commands has multiple terms
- Use groups inside /DIAL

## 0.33.0

- Add option --use-python-env to dodo env
- Fix: return type of load_named_layers
- Fix: tests
- Remove remove_trailing_dashes
- Add sh_cmd
- Add dial command

## 0.32.0

- Update docs
- Add `remove` flag to DecoratorScope
- Add arg --alt to commit-config
- Several fixes related to previous refactoring
- Fix: print-config <key> without leading slash

## 0.31.1

- Update docs
- Fix: always add shebang in dodo script
- Fix: meta_data_filename()
- Add --as option to install-commands
- Remove --create-scd argument from bootstrap

## 0.30.7

- Lots of refactoring and minor fixes
- Improve documentation
- Reintroduce --next-to in new-command
- Use /LAYERS and /LAYER_GROUPS
- Put inferred commands in root layer
- Rename Dodo.get_config to Dodo.get
- Rename to DOCKER_OPTIONS and DOCKER_IMAGES
- Use DOCKER_COMPOSE/cwd

## 0.29.1

- Allow to inspect multiple Docker containers
- Fix dodo menu (28 minutes ago) <Maarten Nieber>
- Fix: remove bad use of global keyword

## 0.29.0

- Make new-command interactive (3 months ago) <Maarten Nieber>
- Add docker-inspect command
- Add --find flag to docker-exec
- Fix menu --tmux bug
- Add support for --layer in command alias
- Warn if a layer does not exist when loading the config
- Fix reporting CommandErrors
- Improve output of dodo help

## 0.28.0

- Refactor to use container with facets

## 0.27.3

- Raise an error if the layer alias is unknown
- Always show help if --help is used

## 0.27.2

- Add cache to ConfigIO
- Add aliases chapter to documentation

## 0.27.1

- Add --trace argument

## 0.27.0

- Support use of /DOCKER/options/foo/user
- Use /DOCKER_COMPOSE/src_dir and /DOCKER_COMPOSE/map
- Add argument --user to docker-exec
- Move --confirm and --echo to decorator
- Add --layer argument, layer aliases and inferred commands

## 0.26.0

- Add command docker-compose
- Fix tests
- Add argument '--by-container-name' to docker-commit
- Support argument 'container' in /DOCKER/options
- Use the --confirm flag twice for confirming nested calls
- Add dodo setup command
- Support install system packages via the .meta file
- Add Dockerfile to README.md
- Fix case where pip3.7 is not found but pip3 is found
- Fix: crash in dodo which --projects if this dir does not exist

## 0.25.4

- Use --confirm twice to force confirmation for nested calls to dodo.
- Replace dodo tmux with dodo menu
- Support option workdir in /DOCKER/options
- Fix path to pip

## 0.25.2

- Fix path to pip in install.py
- Add option --interactive to docker-create
- Allow alias to shadow the original command
- The value of settings.editor can now have flags
- Rename option --defaults to --to-defaults
- Let --layer nullify any competing layer in /ROOT/layers
- Fix lookup of a YAML based command

## 0.25.1

- Fix: only use dotenv values in ConfigExpander

## 0.25.0

- Also read aliases from /ROOT/aliases
- Support the --layer option when calling a command
- Add option --git to install-commands
- Add --name argument to register-autocomplete

## 0.24.0

- Drop support for the EVAL postfix in the configuration
- Add --make-default and --remove-default to install-commands
- Rename install-default-commands to install-commands
- Use global commands dir next to default commands dir
- Allow additional arguments in alias
- Print lists of commands in columns

## 0.23.0

- Load dot env files when expanding the config
- Add option --browse to cd.py
- Add argument --replace to docker-create
- Add flag is_daemon to docker decorator
- Add command dodo exec
- Support commands written as YAML files and shell scripts
- Simplify docker-build
- Several small fixes
- Make docker-create a safe command

## 0.22.0

- Remove usage of os.environ["DODO_COMMANDS_PROJECT_DIR"]
- Use safe=True in dodo bootstrap
- Add --project option to dodo which
- Allow to set a value in dodo new-command --create-command-dir

## 0.21.0

- Allow multiple args in dodo --run
- Add dodo tmux --run and --list
- Small fixes to dodo bootstrap
- Add helpful comments to script created with new-command
- Add option --create-commands-dir to dodo new-command
- Fix: sys.exit if not continuing with unsafe command

## 0.20.0

- Use dodo register-autocomplete instead of patching env/bin/activate
- Use --prompt when creating virtualenv in dodo activate
- Check first if virtualenv exists in dodo activate
- Add short version of --echo and --confirm flags
- Also print values of config args when --help is used
- Skip absolute layer paths in `dodo layer`
- Match multiple names when merging docker options
- Fix: return nothing in 'dodo which --config' if no project selected
- Fix: fail earlier in dodo autostart
- Fix: remove created project_dir if dodo activate fails
- Fix: bug when dodo script is called with "python"

## 0.19.1

- Remove Dodo.args and Dodo.config from public API
- Fix calls for printing traceback
- Fix: use unicode in bordered()
- Fix: dodo diagnose

## 0.19.0

- Add config_args to Dodo.parse_args
- Several refactorings
- Add default commands to config if there is no current project
- Rename 'continue?' to 'confirm?'
- Fix case of missing 'decorators'

## 0.18.0

- Fix check_config_version
- Fix bordered() for windows
- Change signature of find-text command
- Ignore empty name option in docker decorator
- Add argument --create-scd to bootstrap
- Move Paths into config.py
- Add dodo rename command

## 0.17.1

- Rename runcmd to run
- Improve output when printing a single value with print-config
- Fix broken tests and remove stray pudb
- Apply yapf

## 0.17.0

- Add drop-in command
- Add Dodo.decorator function
- Move diff.py back to dodo_standard_commands
- Allow to toggle a layer that has a prefix path

## 0.16.6

- Improve documentation

## 0.16.5

- Improve documentation

## 0.16.4

- Improve documentation

## 0.16.3

- Fix issues with file paths under windows
- Add symlink fallback for python 2 on windows

## 0.16.1

- Revert use of pip install -e

## 0.16.0

- Add commit-config command
- Use /ROOT/shared_config_dir to find the shared configuration files
- Prefer os.symlink to 'ln' on windows
- By default install dodo_standard_commands
- Use pip install -e to install dodo_commands in dodo projects
- Fix the new-command command and tests
- Improve text formatting in dodo tmux

## 0.15.1

- Run yapf on all files
- Dodo activate created a wrong config.yaml file

## 0.15.0

- Simplify CommandPath, and rename dodo command modules
- Add flag capture to runcmd
- Move is_interactive argument to the docker options dict
- Dodo layer prints all layer values if no layer name is given
- Use command groups in dodo tmux

## 0.14.4

- Refactor dodo tmux command and move to standard_commands
- Make naming of dodo command scripts consistent
- Fix spurious parentheses in console output
- Fix spurious parentheses in console output

## 0.14.3

- Several refactorings
- Bugfixes related to the 0.14.0 refactoring
- Fixed a few tests that were no longer green

## 0.14.2

- Update documentation

## 0.14.1

- Update documentation

## 0.14.0

- Add dodo dockerkill command
- Remove --pretty-print option. Instead, print "\" at each line ending
- Remove name argument from dodo dockercommit
- Fix printing a config key with non-string contents
- Replace DodoCommand class with Dodo singleton
- Rename [DodoCommands] to [settings] in global config
- Allow to add aliases in [alias] section of global config
- Set docker instance name to args.service by default
-

## 0.13.5

- Use --image, --name and --command args in 'dodo docker'
- Use sphinx for diagnose output
- Add documentation for the diagnose command
- Remove 'aliases' in /DOCKER/options
- Use 'cwd' key in /DOCKER/options
- Add dockercommit command
- Use volume_map_strict in docker decorator
- Improve reporting of broken config keys

## 0.13.4

- Remove upgrade command
- Add documentation on upgrading
- Replace --name with positional name argument in dodo docker
- Fix: config key may be missing in dockercreate

## 0.13.3

- Support publish_map and publish_list in docker decorator
- Make diff a system command so it can repair broken configurations
- Ask before installing additional packages
- Only require 'deactivate' if using pip in install-default-commands

## 0.13.2

- Fix: keep original command name when using /DOCKER/aliases

## 0.13.1

- Raise an error if no image was found in /DOCKER/options
- Use /DOCKER/aliases in docker decorator

## 0.13.0

- Merge check-config-version command into check-version
- Activate previously active project with "dodo activate -"
- Obtain docker arguments only from /DOCKER/options
- Use /DOCKER/images instead of /DOCKER/image in dockerbuild
- Add dockercreate and dockerexec commands (previously part of webdev_commands)

## 0.12.0

- Fix import path
- Fix args in dockerbuild command
- Add eval command
- Add findtext command
- Add option --kill-existing to docker decorator

## 0.11.6

- Use decorated.docker_image in decorators.docker
- Update README.md

## 0.11.5

- Make value argument optional in dodo global-config

## 0.11.4

- Use decorators.docker.Decorator.get_image_name in DiagnoseBase
- Don't fall back on /DOCKER/image in docker decorator

## 0.11.3

- Fix broken bootstrap command
- Make value arg optional in dodo layer

## 0.11.2

- Use /ROOT/diagnose_dir in dodo diagnose

## 0.11.1

- Add DiagnoseBase class

## 0.11.0

- Allow to use a complex "tuple" key in DOCKER/options
- Add build_args argument to dockerbuild
- Add dodo diagnose command

## 0.10.3

- Remove DOCKER/enabled flag
- Fix crash when there is no docker name
- Add --pretty-print option
- Add option --global-config to dodo which

## 0.10.2

- Add option --src-subdir to bootstrap command
- Fix broken error message in bootstrap
- Allow to get the docker image name from /DOCKER/options
- Add pause decorator

## 0.10.1

- Use semantic_version to compare version strings

## 0.10.0

- Docker decorator adds docker options based on the container name
- Document the use of cookiecutter

## 0.9.4

- Add global-config command
- Remove labels from VERSIONS.md file
- Fix errors in new-command command

## 0.9.3

- Revert the use of glob to find the activate script

## 0.9.2

- Add option --projects to which.py
- Add option --parse to new-command.py
- Add option --link-dir to bootstrap command
- Add option --defaults-dir to diff command
- Use glob to find the location of the activate script

## 0.9.1

- Fix syntax error in layer.py
- Add tests for all standard commands

## 0.9.0

- Allow to call "which" without explicitly using --script or --dir
- Avoid loading all layers multiple times
- Allow wildcards and absolute file paths in the list of layers
- Remove list of decorators from the DodoCommand class

## 0.8.0

- Add optional --project-name to diff command
- Fix the tests, remove the installation test
- Refactor ConfigIO and CommandPath

## 0.7.8

- Replace PyYAML with ruamel.yaml
- Add flag --sudo to dodo upgrade
- Mark commands that do not honor --confirm and --echo as unsafe
- Use /DOCKER/link_list to link containers in docker decorator

## 0.7.7

- Handle case where pip is located inside /usr/local instead of /usr

## 0.7.6

- Print clearer warning in check-version and check-config-version
- Fix broken reference to get_version

## 0.7.5

- Fix crash in install-default-commands when no pip packages are specified

## 0.7.4

- Fix importing missing dependencies via the meta file
- Obtain version with dodo --version
- Move git_commands and webdev_commands to external git repos
- Allow to install pip packages in install-default-commands
- Prevent running dodo upgrade with activated dodo project
- Fix crash in dodo activate when no project is specified

## 0.7.3

- Fix setup.py

## 0.7.2

- Fix setup.py

## 0.7.1

- Write sorted dicts to dodo configuration files

## 0.7.0

- Use a system `dodo` entry point

## 0.6.3

- Replace config-get command by dodo print-config --key
- Use tape instead of tape-run again in tape command
- Add --watch argument to webpack command

## 0.6.2

- Fix remaining broken import

## 0.6.1

- Fix dodo-upgrade (nothing was executed)

## 0.6.0

- Print warning for unexpanded config keys

## 0.5.2

- Fix broken imports

## 0.5.1

- Add check-version command

## 0.5.0

- Improve formatting of errors in the console output
- Add tape command

## 0.4.7

- Add dodo-upgrade command to upgrade dodo_commands itself
- Remove obsolete commands

## 0.4.6

- Fix of error in 0.4.5 (node-sass command)

## 0.4.5

- Small fixes in node-sass and django-manage commands

## 0.4.4

- Improve documentation
- Add node-sass command
- Rename --docker_image to --image in dodo dockerbuild

## 0.4.3

- Remove hack in dodo runpostgres command

## 0.4.2

- Fix crash when latest_project value is missing in global config

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

- symlink dodo_commands in the site-packages of the dodo project
- remove framework and default_commands dirs from dodo project dir

## 0.2.3

- Simplify django-manage command and make it work for Python 2

## 0.2.2

- Add argument --port to docker decorator

## 0.2.1

- Fix: Don't crash on non-standard filenames in /ROOT/layers
- Add optional argument --command to "dodo docker"
- Add argument --res to cd and which commands

## 0.2.0

- Use pip to install dodo_commands
- Many small changes in api

## 0.1.6

- Remove stray pudb invocation in bootstrap command
- Small improvements in commands: django-manage, autoless
- Also disable docker if /DOCKER/enabled equals "False"

## 0.1.5

- New command chown-src
- Better error reporting in gitsplit command
- Configurable python interpreter in django-manage command
- Make directories in \${DOCKER/extra_dirs} available in dockerbuild command
- Use \${/DOCKER/default_cwd} in docker command
- Add argument 'branch' to bootstrap command

## 0.1.4

- Allow to create a project in an existing directory if no dodo_commands directory exists

## 0.1.3

- Allow storing CommandPaths in configuration layers.
- Use symlink dodo_commands/defaults/project in diff command

## 0.1.2

- Store env inside dodo_commands, and config.yaml in dodo_commands/res
- Fix layer and print-config, update README.md to explain configuration layers

## 0.1.1

- Added documentation and fixed broken references to defaults/commands
- Argument --create-from to dodo_activate

## 0.1.0

- Renamed option projects_folder to projects_dir in dodo_commands.config.
- Added option python_interpreter (default=python) to dodo_commands.config. This option sets the python interpreter that is used in the project's virtualenv.
- Changed version back from 1.0.0 to 0.1.0 to indicate beta status
- Several other fixes
- Commands new-command, git-gui, gitk, gitsplit, git, config-get, bootstrap
