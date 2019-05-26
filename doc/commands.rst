.. _commands:

********
Commands
********

Command path
============

The search path for commands is determined by the ``${/ROOT/command_path}`` setting in the project's ``config.yaml``. The ``dodo_system_commands`` module is added to the command path by default. Typically the command path will include:

- one or more packages stored in the ``global commands`` directory. These packages have previously been installed using ``dodo install-commands``.
- all packages stored in the ``default commands`` directory (note the ``*`` wildcard in the example below). By convention, packages in the ``default commands`` directory are symlinks to packages in the ``global commands`` directory.
- packages that are local to the project (note the :code:`special_commands` directory in the example below):

.. code-block:: yaml

    ROOT:
        command_path:
        - ~/.dodo_commands/global_commands/dodo_git_commands
        - ~/.dodo_commands/default_commands/*
        - ${/ROOT/src_dir}/special_commands

Installing global command packages
==================================

The global Dodo Commands scripts are stored in :code:`~/.dodo_commands/global_commands`. You can install additional global commands using:

.. code-block:: bash

    # creates a symlink to ``my_commands`` in ``~/.dodo_commands/global_commands/my_commands``
    dodo install-commands /path/to/my_commands

or

.. code-block:: bash

    # adds ``~/.dodo_commands/global_commands/mycommands`` by installing the
    # ``my_commands`` package
    dodo install-global-commands --pip my_commands

By using the ``--defaults`` flag, a symlink to the command package is automatically added to the :code:`~/.dodo_commands/default_commands` directory. You can also create this symlink later using ``dodo install-commands --make-default <package>``, and remove the symlink using ``dodo install-commands --remove-default <package>``.

.. tip::

    Don't use ``dodo install-commands`` for project specific command scripts. Instead, store them inside the project's source tree, and reference them directly in the ``/ROOT/command_path`` node of the configuration file.

Excluding directories from the command path
===========================================

Use ``${/ROOT/command_path_exclude}`` to exclude certain paths from the command path:

.. code-block:: yaml

    ROOT:
        command_path_exclude:
        - ~/.dodo_commands/default_commands/foo


Importing symbols from another module
=====================================

In your Dodo command script, you can import a symbol from another module in the command path using (for example) ``import foo from dodo_my_commands.bar``. Note that the names of the modules in the command path must be unique. Also, it is required that ``dodo_my_commands`` exists in the active project's command path, otherwise the import will fail.


Specifying command dependencies in the .meta file
=================================================

Each Dodo command should ideally run out-of-the-box. If your ``foo`` command needs additional Python packages, you can describe them in a ``foo.meta`` file:

.. code-block:: yaml

    requirements:
    - dominate==2.2.0

In this example, calling the ``foo`` command will ask the user for confirmation to automatically install the ``dominate`` package into the python virtual environment of the active Dodo Commands project.


Aliases
=======

You can added aliases for any dodo command in the ``aliases`` section of :ref:`global_config`, e.g.

.. code-block:: ini

    [alias]
    wh = which
    whpp = which --projects
    pc = print-config
