.. _how-it-works:

**********************************
How the Dodo Commands system works
**********************************

After following the :ref:`installation` steps, you now have a ``dodo`` executable that you can use to create new projects in the projects directory. To see where it's located type:

.. code-block:: bash

    which dodo

Each dodo project has it's own copy of the dodo executable (called the "project" dodo). By calling the "project" dodo, you can operate on the project. We'll explain how this works the long and clunky way, and then how the same can be done much faster.


Creating a project
==================

Projects are created with the ``dodo activate`` command::

    dodo activate FooBar --create

Running this command creates a new FooBar project directory with various files. The most important one is the ``~/projects/FooBar/dodo_commands/env/bin/dodo`` script file. This copy of the ``dodo`` script is specific to the created project. When you call this ``dodo`` script, it's implied that you are operating on the ``FooBar`` project.

Running a command
=================

You run a command on a project by calling its ``dodo`` script with the name of the command:

    ~/projects/FooBar/dodo_commands/env/bin/dodo foo --bar

This call will execute the following steps:

#. the ``dodo`` script will read the ``command_path`` (a list of directories with command scripts) from the project's configuration file (``~/projects/FooBar/dodo_commands/res/config.yaml``).

#. the foo.py script is found and run with the --bar option

#. the foo.py script can access the project configuration and does some operation on the project (such as deleting all build results in ~/projects/FooBar/build/debug)

Activating a project
====================

The ``~/projects/FooBar/dodo_commands/env/bin/dodo`` script is part of a virtual python environment that was installed when we called ``dodo activate FooBar --create``. You can save some typing by first activating this python environment with:

.. code-block:: bash

    source ~/projects/FooBar/dodo_commands/env/bin/activate

This has the effect that running ``dodo`` will now find the project-specific dodo script, rather than the "system" dodo script. You can now run commands against the activated project with:

.. code-block:: bash

    dodo foo --bar

The short-cut to activating the python environment is using:

.. code-block:: bash

    $(dodo activate FooBar)

This works because the ``dodo activate`` call prints the line ``source ~/projects/FooBar/dodo_commands/env/bin/activate`` to the console, and the ``$(...)`` syntax takes care of executing this in the shell. To create a new project and activate it at the same time, call:

.. code-block:: bash

    $(dodo activate FooBar --create)

If you activated a project and you want to go back to the previously active project, run ``$(dodo activate -)``.

.. _autostart:

Activating the last used project
================================

Dodo Commands remembers which project was last activated. You can activate the last used project with ``$(dodo activate --latest)``. It's usually convenient to activate the latest project whenever you open a terminal. To facilitate this, you can call ``dodo autostart on`` to write a small script file to ``~/.dodo_commands_autostart``.

.. code-block:: bash

    dodo autostart on
    cat ~/.dodo_commands_autostart

    > $(dodo activate --latest)
    > dodo check-config-version
    > dodo check-version

Add the following lines to your ``~/.bashrc`` to execute this script when a terminal is opened:

.. code-block:: bash

    if [ -f ~/.dodo_commands_autostart ]; then
        . ~/.dodo_commands_autostart
    fi

If you want to disable the autostart behaviour, call ``dodo autostart off``. This will delete the ``~/.dodo_commands_autostart`` file, and therefore disable the automatic project activation.
