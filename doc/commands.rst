.. _commands:

********
Commands
********

Command paths and default commands
==================================

The default Dodo Commands scripts are stored in :code:`~/.dodo_commands/default_commands`. These commands are available in any Dodo Commands project you create. You can install additional default commands using:

.. code-block:: bash

    # creates a symlink to ``my_commands`` in ``~/.dodo_commands/default_commands/my_commands``
    dodo install-default-commands /path/to/my_commands

or

.. code-block:: bash

    # adds ``~/.dodo_commands/default_commands/mycommands`` by installing the
    # ``my_commands`` package
    dodo install-default-commands --pip my_commands

The search path for commands is determined by the ``${/ROOT/command_path}`` setting in config.yaml:

.. code-block:: yaml

    ROOT:
        command_path:
        - - ~/.dodo_commands
          - default_commands/*

Each item in ``${/ROOT/command_path}`` is itself a list of two elements:

- a prefix path that is added to :code:`sys.path`
- a postfix path that must be importable as a python module

In the example below, all subdirectories of the default commands are used (note the ``*`` wildcard), as well as the :code:`special_commands` directory:

.. code-block:: yaml

    ROOT:
        command_path:
        - - ~/.dodo_commands
          - default_commands/*
        - - ${/ROOT/src_dir}
          - special_commands

In this case, the final command_path contains ``~/projects/FooBar/src/special_commands``, ``~/.dodo_commands/default_commands/standard_commands`` and ``~/.dodo_commands/default_commands/mycommands``.

Use ``${/ROOT/command_path_exclude}`` to exclude certain paths from the command path:

.. code-block:: yaml

    ROOT:
        command_path_exclude:
        - - ~/.dodo_commands
          - default_commands/foo


System commands
===============

System commands such as ``dodo activate`` are part of the ``dodo_commands.system_commands`` python package. An entry for these commands is added automatically to the command path (you can inspect this with ``dodo print-config ROOT/command_path``).


Specifying command dependencies in the .meta file
=================================================

Each Dodo command should ideally run out-of-the-box. If your ``foo`` command needs additional Python packages, you can describe them in a ``foo.meta`` file:

.. code-block:: yaml

    requirements:
    - dominate==2.2.0

In this example, calling the ``foo`` command will automatically install the ``dominate`` package into the python virtual environment of the active Dodo Commands project.


The structure of a command script
=================================

When you run a command with ``dodo foo --bar``, the foo.py script is searched in the configured command_path, as described above, and imported. This import will not have any effect if you are using a standard ``if __name__ == '__main__'`` clause. Therefore, you should instead use ``if Dodo.is_main(__name__)``, as explained in :ref:`singleton`. Apart from this restriction, you can do anything you like in the script. To take advantage of the Dodo Command features, read about the Dodo singleton (:ref:`singleton`).
