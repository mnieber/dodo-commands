# Dodo Commands

## Introduction

Dodo Commands is a small framework for creating separated development environments for your projects. Each development environment contains:

- a Python virtual environment
- a set of short commands
- a configuration file with project specific parameters
- optionally, some docker images

## Documentation

- [Read the docs](http://dodo-commands.readthedocs.io/en/latest/?)

## License

MIT License (see the enclosed license file).

## Rationale

1. Each project has a Python virtual environment, which separates it from other projects.

Call `$(dodo activate fooProject)` to activate its Python virtual environment.

2. Each project contains a set of short commands. This allows you to run common operations quickly without having to remember too much about them.

For example, you may call `dodo cmake` to invoke the cmake executable in the project's C++ build directory. It's enough to type `dodo cmake` because all other required information (the list of cmake flags and the desired C++ source directory) is read from the project's configuration file.

3. If you switch to a different project with `$(dodo activate barProject)`, you still call `dodo cmake` to invoke the cmake compiler, but now the C++ build directory location and cmake parameters are read from `barProject`'s configuration file.

4. If you enable docker support for `fooProject`, then it will run the cmake executable in the pre-configured docker container. This allows you to keep your runtime environments isolated from your host computer.

## Example

The following steps install a pre-existing Dodo Commands project that offers a `dodo cmake` command:

0. Install the Dodo Commands tool
    ```bash
    > sudo apt-get install python-virtualenv git
    > pip install dodo_commands
    ```

1. Create a new (empty) `dodo_tutorial` project and bootstrap it by copying some configuration files from the pre-existing `dodo_commands_tutorial` project

    ```bash
    > $(dodo activate dodo_tutorial --create)
    > dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/mnieber/dodo_commands_tutorial.git
    ```

2. Do a trial run of the cmake command, without actually running it:

    ```bash
    > dodo cmake --confirm
    ```

    which returns

    ```bash
    (/root/projects/dodo_tutorial/build/release) cmake -DCMAKE_BUILD_TYPE=release -DCMAKE_INSTALL_PREFIX=/root/projects/dodo_tutorial/install /root/projects/dodo_tutorial/src

    confirm? [Y/n]
    ```

3. The command line arguments in the cmake invocation come from the configuration file. This can be inspected by using `dodo print-config` to print the settings in the `/CMAKE` configuration node:

    ```bash
    > dodo print-config /CMAKE
    ```

    which returns

    ```yaml
    variables:
        CMAKE_BUILD_TYPE: release
        CMAKE_INSTALL_PREFIX: ${/ROOT/project_dir}/install
    ```

Note that you can run `dodo print-config` to show the entire configuration.

4. To understand how Dodo Commands created the cmake invocation, you can inspect the code of the 'cmake' command script with:

    ```bash
    > cat $(dodo which cmake)
    ```

    which returns

    ```python
    from argparse import ArgumentParser
    from dodo_commands.framework import Dodo


    def _args():  # noqa
        parser = ArgumentParser(description='Configure code with CMake')
        args = Dodo.parse_args(parser)
        args.src_dir = Dodo.get_config("/ROOT/src_dir")
        args.build_dir = Dodo.get_config("/ROOT/build_dir")
        return args


    if Dodo.is_main(__name__):
        args = _args()
        Dodo.runcmd(
            ["cmake"] +
            [
                "-D%s=%s" % x for x in
                Dodo.get_config('/CMAKE/variables').items()
            ] +
            [args.src_dir],
            cwd=args.build_dir
        )
    ```

5. To create a new command, just use

    ```bash
    # this call will return the filename of the create command script
    > dodo new-command foo --next-to cmake
    ```


6. (Advanced) Show the command line for running cmake in docker:

    ```bash
    # enable the docker.on.yaml configuration layer that adds some docker specific
    # values (such as the image name) to the configuration file
    > dodo layer docker on

    # Inspect the changes to the configuration introduced by the new layer
    > dodo print-config /DOCKER

    # The same command now runs in docker!
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

    confirm? [Y/n]
    ```

    ```bash

    # build the dodo_tutorial:1604 image so that the docker command will succeed
    > dodo docker-build --confirm base
    ```

This simple scenario shows how a complicated command line can be compressed into a short command that's easy to remember. We've seen that by offering the `--confirm` flag Dodo Commands is transparent about what it actually executes. It's also easy to get new colleagues started on a project by sharing your command scripts and configuration file with them (see [the documentation](http://dodo-commands.readthedocs.io/en/latest/sharing-projects.html) for details).

## Example as a Dockerfile

Below, we show the same steps in a Dockerfile. It's added for convenience: you can build it, run it, and play around. When you run this image and a bash shell is created, call ``$(dodo activate dodo_tutorial)`` to active the virtual environment of the ``dodo_tutorial`` project.

    ```bash
    # This Dockerfile has *only one* purpose: to show the steps of the tutorial
    # in https://github.com/mnieber/dodo_commands/blob/master/README.md.
    # 
    # Please, don't get confused. This docker image is not used for installing
    # and running Dodo Commands. For normal usage, you should install 
    # Dodo Commands on the host computer, not inside a container.

    FROM python:3.7-slim-stretch

    RUN apt-get update && apt-get install -y cmake python-virtualenv git
    RUN pip3 install dodo_commands

    # Normally, you would run $(dodo activate dodo_tutorial --create)
    # to activate the newly created virtual environment. Here, we instead
    # set the virtualenv's env/bin directory as the working directory.

    RUN dodo activate dodo_tutorial --create
    WORKDIR /root/projects/dodo_tutorial/dodo_commands/env/bin

    RUN ./dodo bootstrap src extra/dodo_commands/res \
        --force \
        --git-url https://github.com/mnieber/dodo_commands_tutorial.git

    RUN ./dodo cmake --echo

    RUN ./dodo print-config CMAKE

    RUN cat $(./dodo which cmake)

    RUN ./dodo new-command foo --next-to cmake

    RUN ./dodo layer docker on
    RUN ./dodo print-config DOCKER
    RUN ./dodo cmake --echo

    RUN ./dodo docker-build --echo base

    CMD /bin/bash
    ```
