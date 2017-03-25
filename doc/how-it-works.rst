.. _how-it-works:

**********************************
How the Dodo Commands system works
**********************************

After following the :ref:`installation` steps, you can create new projects in the projects directory and work with them. We'll explain how it works the long and clunky way, and then how the same can be done faster.

System dodo script
==================

The entry point for running dodo commands is the ``dodo`` script. To see where it's located type:

.. code-block:: bash

    which dodo

In a minute we'll learn that each Dodo Commands project has it's own copy of the ``dodo`` script. When you are working on a Dodo Commands project, you will use the "project" dodo, and otherwise the "system" dodo. Though in practice these scripts work the same, and you will not notice a difference in behaviour, it's important to understand this distinction.

Creating a project
==================

Projects are created with the ``dodo activate`` command::

    dodo activate FooBar --create

Running this command creates a new FooBar project directory with various files. The most important one is the ``~/projects/FooBar/dodo_commands/env/bin/dodo`` script file. This is a version of the ``dodo`` script that is specific to the created project. When you call this ``dodo`` script, it's implied that you are operating on the ``FooBar`` project.

Running a command
=================

You run a command on a project by calling its ``dodo`` script with the name of the command:

~/projects/FooBar/dodo_commands/env/bin/dodo foo --bar

This call will execute the following steps:

#. the dodo script will load the ``command_path`` (a list of directories with command scripts) from the project's configuration file (``~/projects/FooBar/dodo_commands/res/config.yaml``).

#. the foo.py script is found and run with the --bar option

#. the foo.py script reads the project configuration and does some operation on the project (such as deleting all build results in ~/projects/FooBar/build/debug)

Activating a project
====================

The ``~/projects/FooBar/dodo_commands/env/bin/dodo`` script is part of a virtual python environment that was installed when we called ``dodo activate FooBar --create``. You can save some typing by first activating this python environment with:

.. code-block:: bash

    source ~/projects/FooBar/dodo_commands/env/bin/activate

This has the effect that running ``dodo`` will find the project-specific script, rather than the "system" dodo script. You can now run commands against the activated project with:

.. code-block:: bash

    dodo foo --bar

The short-cut to activating the python environment is using:

.. code-block:: bash

    $(dodo activate FooBar)

The way this works is that the ``dodo activate`` command prints the line ``source ~/projects/FooBar/dodo_commands/env/bin/activate`` to the console, and the ``$(...)`` syntax takes care of executing this in the shell. To create a new project and activate it at the same time, call:

.. code-block:: bash

    $(dodo activate FooBar --create)


Activating the last used project
================================

Dodo Commands remembers which project was last activated. You can activate the last used project with ``$(dodo activate --latest)``. It's usually convenient to activate the latest project whenever you open a terminal. Calling ``dodo autostart on`` writes a small script file to ``~/.dodo_commands_autostart``.

.. code-block:: bash

    dodo autostart on
    cat ~/.dodo_commands_autostart

    > $(dodo activate --latest)
    > dodo check-config-version

Add the following lines to your ``~/.bashrc`` to execute this script when a terminal is opened:

.. code-block:: bash

    if [ -f ~/.dodo_commands_autostart ]; then
        . ~/.dodo_commands_autostart
    fi

If you want to disable the autostart behaviour, call ``dodo autostart off``. This will delete the ``~/.dodo_commands_autostart`` file.
