.. _commands:

********
Commands
********

Command paths and default commands
==================================

The default Dodo command scripts are stored in :code:`~/.dodo_commands/default_commands`. You can install additional default commands using:

.. code-block:: bash

    # creates a symlink to ``my_commands`` in ``~/.dodo_commands/default_commands/my_commands``
    dodo install-default-commands /path/to/my_commands

or

.. code-block:: bash

    # adds ``~/.dodo_commands/default_commands/mycommands`` by installing the
    # ``my_commands`` package
    dodo install-default-commands --pip my_commands

All search paths for commands are specified by the ${/ROOT/command_path} setting in config.yaml:

    ROOT:
        command_path:
        - - ~/.dodo_commands
          - default_commands/*

Each item in the ${/ROOT/command_path} is itself a list of two elements:

- a prefix path that is added to :code:`sys.path`
- a postfix path that must be importable as a python module

In the example below, the default commands are used as well as the
:code:`special_commands` directory:

.. code-block:: yaml

    ROOT:
        # final command_path is:
        # - ~/projects/FooBar/src/special_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/standard_commands
        # - ~/projects/FooBar/dodo_commands/default_commands/mycommands
        command_path:
        - - ${/ROOT/src_dir}
          - special_commands
        - - ~/.dodo_commands
          - default_commands/*

Use ${/ROOT/command_path_exclude} to exclude parts of the command path:

.. code-block:: yaml

    ROOT:
        command_path_exclude:
        - - ~/.dodo_commands
          - default_commands/foo


Specifying command dependencies in the .meta file
=================================================

Each Dodo command should ideally run out-of-the-box. If your ``foo`` command needs additional Python packages, you can describe them in a ``foo.meta`` file:

.. code-block:: yaml

    requirements:
    - dominate==2.2.0

System commands
===============

The system commands such as ``dodo activate`` are part of the ``dodo_commands.system_commands`` python package. An entry for these commands is added automatically to the command path (you can inspect this with ``dodo print-config``).

Installing command directories from dodo_commands.extra
=======================================================

If you call :code:`dodo install-default-commands` with a path that is not found, then :code:`dodo install-default-commands` will try to locate this path inside the `extra` directory of the dodo_commands python package. Calling :code:`dodo install-default-commands --help` will show a list of command directories that come standard with the dodo_commands package.


The BaseCommand class
=====================

When you run a command with :code:`dodo foo --bar`, the foo.py script is searched in the configured command_path, as described above. The foo.py script:

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
