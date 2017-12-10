# Dodo Commands

By Maarten Nieber, with contributions from Georg Rollinger.

## Introduction

Dodo Commands is a small framework for creating separate development environments for your projects. Each development environment contains:

- a Python virtual environment
- a set of short commands
- a configuration file with project specific parameters
- optionally, some docker images

## Documentation

- [Read the docs](http://dodo-commands.readthedocs.io/en/latest/?)

## License

MIT License (see the enclosed license file). Files that are based on source code from the Django Software Foundation contain a copy of the associated license at the start of the file.

## Rationale

1. Each project has a separate Python environment, which separates it from other projects.

Call `$(dodo activate fooProject)` to activate its Python virtual environment.

2. Each project contains a set of short commands. This allows you to run common operations quickly without having to remember too much about them.

For example, you may call `dodo cmake` to invoke the cmake executable in the project's C++ build directory, passing it a list of flags and the desired C++ source directory. It's enough to type `dodo cmake` because all other required information is read from the project's configuration file.

3. If you switch to a different project with `$(dodo activate barProject)`, you still call `dodo cmake` to invoke the cmake compiler, but now the C++ build directory location and cmake parameters are read from `barProject`'s configuration file.

4. If you enable docker support for `fooProject`, then it will run the cmake executable in the pre-configured docker container. This allows you to keep your runtime environments isolated from your host computer.

## Example

The following steps show a Dodo Commands project that offers a `dodo cmake` command:

0. Install
    ```bash
    > sudo apt-get install python-virtualenv git
    > pip install dodo_commands
    > dodo install-default-commands standard_commands
    ```

1. Create a new (empty) `dodo_tutorial` project and bootstrap it by copying some configuration files from the `dodo_commands_tutorial` project

    ```bash
    > $(dodo activate dodo_tutorial --create)
    > dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/mnieber/dodo_commands_tutorial.git
    ```

2. Inspect the configuration file:

    ```bash
    > cat $(dodo which --config)
    ```

    which returns

    ```yaml
    CMAKE:
      variables:
        CMAKE_BUILD_TYPE: release
        CMAKE_INSTALL_PREFIX: ${/ROOT/project_dir}/install

    ROOT:
      build_dir: ${/ROOT/project_dir}/build/${/CMAKE/variables/CMAKE_BUILD_TYPE}
      src_dir: ${/ROOT/project_dir}/src
      command_path:
      - - ~/.dodo_commands/
        - default_commands/*
      - - ${/ROOT/src_dir}/extra/dodo_commands
        - tutorial_commands
      version: 1.0.0
    ```

3. If you inspect the code of the 'cmake' command script with:

    ```bash
    > cat $(dodo which --script cmake)
    ```

    you will see that it refers to configuration file values such as `/ROOT/build_dir`:

    ```python
    """Configure code with CMake."""
    from dodo_commands.system_commands import DodoCommand

    class Command(DodoCommand):  # noqa
        docker_options = [('name', 'cmake')]

        def handle_imp(self, **kwargs):  # noqa
            self.runcmd(
                ["cmake"] +
                [
                    "-D%s=%s" % x for x in
                    self.get_config('/CMAKE/variables').items()
                ] +
                [self.get_config("/ROOT/src_dir")],
                cwd=self.get_config("/ROOT/build_dir")
            )
    ```

4. Do a trial run of the cmake command, without actually running it:

    ```bash
    > dodo cmake --confirm
    ```

    which returns

    ```bash
    (/root/projects/dodo_tutorial/build/release) cmake -DCMAKE_BUILD_TYPE=release -DCMAKE_INSTALL_PREFIX=/root/projects/dodo_tutorial/install /root/projects/dodo_tutorial/src

    continue? [Y/n]
    ```

5. Show the command line for running cmake in docker:

    ```bash
    # enable the docker.on.yaml configuration layer that adds some docker specific
    # values (such as the image name) to the configuration file
    > dodo layer docker on

    # the same command now runs in docker!
    > dodo cmake --confirm
    ```

    which returns

    ```bash
    (/root/projects/dodo_tutorial/dodo_commands/res) docker run
      --rm --interactive --tty
      --name=cmake
      --workdir=/root/projects/dodo_tutorial/build/release
      dodo_tutorial:1604
      cmake -DCMAKE_BUILD_TYPE=release -DCMAKE_INSTALL_PREFIX=/root/projects/dodo_tutorial/install /root/projects/dodo_tutorial/src

    continue? [Y/n]
    ```

    Note that this command line only works if the dodo_tutorial:1604 image exists. You can build it by running `dodo dockerbuild`.


This simple scenario shows how a complicated command line can be compressed into a short command that's easy to remember. We've seen that Dodo Commands is transparent about what it actually executes. It's also easy to get new colleagues started on a project by sharing your command scripts and configuration file with them (see [the documentation](http://dodo-commands.readthedocs.io/en/latest/sharing-projects.html) for details).
