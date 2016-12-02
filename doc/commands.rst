.. _commands:

********
Commands
********

Command paths and default commands
==================================

The default Dodo command scripts are stored in :code:`dodo_commands/defaults/commands`. Each project contains a symlink to this directory (e.g. the FooBar project stores a link to this directory in :code:`~/projects/FooBar/default_commands`). You can install additional default commands using:

.. code-block:: bash

    # adds a subdirectory dodo_commands/defaults/commands/mycommands
    dodo-install-defaults --git --commands https://github.com/foo/mycommands.git

Besides the default_commands directory, a project can specify additional search paths for commands. This is done using the ${/ROOT/command_path} setting in config.yaml:

.. code-block:: yaml

    ROOT:
        # final command_path is:
        # - ~/projects/FooBar/src/special_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/standard_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/mycommands
        command_path:
        - src/special_commands
        - dodo_commands/default_commands/*

Each directory in command_path is relative to the project directory, and should point to a Python module.
Use ${/ROOT/command_path_exclude} to exclude parts of the command path:

.. code-block:: yaml

    ROOT:
        command_path:
        - dodo_commands/default_commands/*
        command_path_exclude:
        - dodo_commands/default_commands/foo

Extending sys.path using the command_path
=========================================

In the default case, as mentioned above, directories in ${/ROOT/command_path} are Python modules. This means that each intermediate node in the directory must contain a :code:`__init__.py` file. An alternative is to supply a pair of values: :code:`[sys_dir, module_dir]`. The first part (sys_dir) is added to :code:`sys.path`, and the second part (module_dir) should be a Python module:

.. code-block:: yaml

    ROOT:
        command_path:
        # ${/ROOT/project_dir}/src/foo is added to sys.path
        # extra commands are found in ${/ROOT/project_dir}/src/foo/bar/foo_commands
        - ["src/foo", "bar/foo_commands"]

The BaseCommand class
=====================

When you run a command with :code:`dodo foo --bar`, the foo.py script is searched in the configured command_path,
as described above. The foo.py script:

- should declare a :code:`Command` class that derives from :code:`BaseCommand`
- can override :code:`add_arguments` to add more arguments to the command
- should override :code:`handle` to implement the command action
- can call :code:`self.get_config` to get configuration values

The following example illustrates this.

.. code-block:: python

    from dodo_commands.framework import BaseCommand

    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                '--bar',
                action="store_true",
            )

        def handle(self, bar, **kwargs):
            project_dir = self.get_config("/ROOT/project_dir")
            sys.stdout.write("bar=%d" % bar)
