# Dodo Commands

By Maarten Nieber, with contributions from Georg Rollinger.

## Introduction

Dodo Commands is a small framework for creating separate development environments for your projects. Each development environment contains:

- a Python virtual environment
- a set of associated command scripts (shareable among projects, if you wish)
- a set of configuration files that contain project specific parameters

## Documentation

- [Read the docs](http://dodo-commands.readthedocs.io/en/latest/?)

## License

MIT License (see the enclosed license file). Files that are based on source code from the Django Software Foundation contain a copy of the associated license at the start of the file.

## Rationale

Dodo Commands offers a structured way to keep separated work environments for your projects:

- each project has its own associated command scripts, configuration files and python environment
- you run these commands from a single entry point (so you don't have to remember script locations)
- command script can refer to project configuration values, so you can separate logic from configuration
- you can turn on/off extra configuration layers that override your basic configuration values. This allows you - for example - to quickly switch between different C++ compilers.
- auto-completion is provided for the command script names and their arguments (when using bash)

This can be illustrated by the following use-case:

- you want to configure your various C++ projects using cmake
- each C++ project uses some specific cmake flags
- the target directory depends on the project folder and the CMAKE_BUILD_TYPE flag (debug or release)
- to guarantee reproducable results, you want to configure and compile your C++ code in a Docker container

The following steps shows how this is accomplished with Dodo Commands:

1. Install

    ```bash
    > pip install dodo_commands
    ```

2. enable the standard commands and tutorial projects

    ```bash
    > dodo install-default-commands standard_commands
    ```

3. create a new dodo_tutorial project

    ```bash
    > $(dodo activate dodo_tutorial --create)
    ```

4. Use `dodo bootstrap` to obtain the tutorial configuration files

    ```bash
    > dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/mnieber/dodo_commands_tutorial.git
    ```

5. inspect the configuration file of the dodo_tutorial project. This configuration provides the necessary input parameters for cmake and docker:

    ```bash
    > cat $(dodo which --config)
    ```

    which returns

    ```yaml
    CMAKE:
        variables:
            CMAKE_BUILD_TYPE: release
            CMAKE_INSTALL_PREFIX: ${/ROOT/project_dir}/install

    DOCKER:
        enabled: true
        image: dodo_tutorial:1604
        volume_map:
            ${/ROOT/project_dir}/log: /var/log

    ROOT:
        build_dir: ${/ROOT/project_dir}/build/${/CMAKE/variables/CMAKE_BUILD_TYPE}
        src_dir: ${/ROOT/project_dir}/src
        command_path:
        - - ~/.dodo_commands/
          - default_commands/*
        - - ${/ROOT/project_dir}
          - dodo_commands/commands
        version: 1.0.0
    ```

6. inspect the code of the 'cmake' command script. Note that this script does not contain project specific values, which means it's reusable:

    ```bash
    > cat $(dodo which --script cmake)
    ```

    which returns

    ```python
    """Configure code with CMake."""
    from dodo_commands.extra.standard_commands import DodoCommand

    class Command(DodoCommand):  # noqa
        decorators = ['docker']

        def _get_variable_list(self, prefix):
            return [
                prefix + "%s=%s" % key_val for key_val in
                self.get_config('/CMAKE/variables').items()
            ]

        def handle_imp(self, **kwargs):  # noqa
            self.runcmd(
                ["cmake"] +
                self._get_variable_list("-D") +
                [self.get_config("/ROOT/src_dir")],
                cwd=self.get_config("/ROOT/build_dir")
            )
    ```

7. build the docker image that is associated with the dodo_tutorial project

    ```bash
    > dodo dockerbuild
    ```

8. enable the debug.on.yaml layer

    ```bash
    # check value of CMAKE_BUILD_TYPE
    # returns 'release'
    > dodo print-config --key /CMAKE/variables/CMAKE_BUILD_TYPE

    > dodo layer debug on

    # returns ['debug.on.yaml']
    > dodo print-config --key /ROOT/layers

    # returns 'debug'
    > dodo print-config --key /CMAKE/variables/CMAKE_BUILD_TYPE

    ```

9. do a trial run of the cmake command, without actually running it:

    ```bash
    > dodo cmake --confirm
    ```

    which returns

    ```bash
    (/home/maarten/projects/dodo_commands) /usr/bin/docker run --rm -w /home/maarten/projects/dodo_tutorial/build/debug -i -t --volume=/home/maarten/projects/dodo_tutorial/log:/var/log dodo_tutorial:1604 cmake -DCMAKE_INSTALL_PREFIX=/home/maarten/projects/dodo_tutorial/install -DCMAKE_BUILD_TYPE=debug /home/maarten/projects/dodo_tutorial/src

    continue? [Y/n]
    ```

This simplified scenario already shows how a complicated command line can be compressed into a short command. Instead of remembering/editing long command lines, you can tweak your project configuration files and produce these long command lines with Dodo Commands. It's also easy to get new colleagues started on a project by sharing your command scripts and configuration file with them (see [the documentation](http://dodo-commands.readthedocs.io/en/latest/sharing-projects.html) for details).
