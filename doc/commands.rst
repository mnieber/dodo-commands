.. _commands:

********
Commands
********

Command path
============

The search path for commands is determined by the ``${/ROOT/command_path}`` setting in ``config.yaml``. The ``dodo_system_commands`` module is added to the command path by default. In the example below, all subdirectories of the default commands directory are used (note the ``*`` wildcard), as well as the :code:`special_commands` directory:

.. code-block:: yaml

    ROOT:
        command_path:
        - ~/.dodo_commands/default_commands/*
        - ${/ROOT/src_dir}/special_commands

Default commands
================

The default Dodo Commands scripts are stored in :code:`~/.dodo_commands/default_commands`. As we saw above, the default commands are made available by adding ``~/.dodo_commands/default_commands/*`` to the command path (this is done by default when you create a new project). You can install additional default commands using:

.. code-block:: bash

    # creates a symlink to ``my_commands`` in ``~/.dodo_commands/default_commands/my_commands``
    dodo install-default-commands /path/to/my_commands

or

.. code-block:: bash

    # adds ``~/.dodo_commands/default_commands/mycommands`` by installing the
    # ``my_commands`` package
    dodo install-default-commands --pip my_commands


Excluding directories from the command path
===========================================

Use ``${/ROOT/command_path_exclude}`` to exclude certain paths from the command path:

.. code-block:: yaml

    ROOT:
        command_path_exclude:
        - - ~/.dodo_commands/default_commands/foo


Importing symbols from another module
=====================================

In your Dodo command script, you can import a symbol from another module in the command path using (for example) ``import foo from dodo_my_commands.bar``. Note that the names of the modules in the command path must be unique. Also, it is now required that ``dodo_my_commands`` exists in the command path, otherwise the import will fail.


Specifying command dependencies in the .meta file
=================================================

Each Dodo command should ideally run out-of-the-box. If your ``foo`` command needs additional Python packages, you can describe them in a ``foo.meta`` file:

.. code-block:: yaml

    requirements:
    - dominate==2.2.0

In this example, calling the ``foo`` command will (after asking the user for confirmation) automatically install the ``dominate`` package into the python virtual environment of the active Dodo Commands project.


Aliases
=======

You can added aliases for any dodo command in the ``aliases`` section of :ref:`global_config`, e.g.

.. code-block:: ini

    [alias]
    wh = which
    pc = print-config
