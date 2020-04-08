# Dodo Commands

## Introduction

Dodo Commands is a small framework for creating separated development environments for your projects. Each development environment contains:

- a project directory
- a set of short commands
- a configuration file with project specific parameters
- optionally, a Python virtual environment
- optionally, some docker images

## Documentation

- [Read the docs](http://dodo-commands.readthedocs.io/en/stable/?)

## License

MIT License (see the enclosed license file).

## Rationale

1. Each project has a Python virtual environment, which separates it from other projects.

Call `$(dodo env fooProject)` to activate its Python virtual environment.

2. Each project contains a set of short commands. This allows you to run common operations quickly without having to remember too much about them.

For example, you may call `dodo cmake` to invoke the cmake executable in the project's C++ build directory. It's enough to type `dodo cmake` because all other required information (the list of cmake flags and the desired C++ source directory) is read from the project's configuration file.

3. If you switch to a different project with `$(dodo env barProject)`, you still call `dodo cmake` to invoke the cmake compiler, but now the C++ build directory location and cmake parameters are read from `barProject`'s configuration file.

4. If you enable docker support for `fooProject`, then it will run the cmake executable in the pre-configured docker container. This allows you to keep your runtime environments isolated from your host computer.

To learn more, try out the [tutorial](https://dodo-commands.readthedocs.io/en/stable/#tutorial)