.. _commands:

********
Commands
********

Command paths and default commands
==================================

The default Dodo command scripts are stored in :code:`dodo_commands/defaults/commands`. Each project contains a symlink to this folder (e.g. the FooBar project stores a link to this folder in :code:`~/projects/FooBar/default_commands`). You can install additional default commands using:

.. code-block:: bash

    # adds a subfolder dodo_commands/defaults/commands/mycommands
    dodo-install-defaults --commands https://github.com/foo/mycommands.git

Besides the default command paths, a project can specify additional search paths for commands. This is done using the ${/ROOT/command_paths} setting in config.yaml:

.. code-block:: yaml

    ROOT:
        # final command_paths are:
        # - ~/projects/FooBar/src/special_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/standard_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/mycommands
        command_paths:
        - src/special_commands
        - dodo_commands/default_commands/*

Each path in command_paths is relative to the project directory, and should point to a Python module.

Extending sys.path using command_paths
======================================

In the default case, as mentioned above, paths in ${/ROOT/command_paths} are Python modules. This means that each (intermediate) sub-folder in the path must contain a :code:`__init__.py` file. An alternative is to supply a pair of values: :code:`[sys_path, module_path]`. The first part (sys_path) is added to :code:`sys.path`, and the second part (module_path) should be a Python module:

.. code-block:: yaml

    ROOT:
        command_paths:
        # ${/ROOT/project_dir}/src/foo is added to sys.path
        # extra commands are found in ${/ROOT/project_dir}/src/foo/bar/foo_commands
        - ["src/foo", "bar/foo_commands"]
        - dodo_commands/default_commands/*

The BaseCommand class
=====================

When you run a command with :code:`dodo foo --bar`, the foo.py script is searched in the configured list of command_paths, as described above. The foo.py script:

- should declare a command class that derives from :code:`BaseCommand`
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
