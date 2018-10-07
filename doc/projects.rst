.. _how-it-works:

***************************
Creating and using projects
***************************

After following the :ref:`installation` steps, you now have a ``dodo`` executable that you can use to create new projects in the projects directory (which is ``~/projects`` by default). To see where it's located type:

.. code-block:: bash

    which dodo

Each dodo project has it's own copy of the dodo executable (called the "project" dodo). By calling the "project" dodo, you can operate on the project. We'll explain how this works the long and clunky way, and then how the same can be done much faster.


Creating a project
==================

Projects are created with the ``dodo activate`` command:

    dodo activate FooBar --create

Running this command creates a new ``~/projects/FooBar`` directory with various files. The most important one is ``~/projects/FooBar/dodo_commands/env/bin/dodo``. This copy of the ``dodo`` script is specific to the created project. Calling it implies that you are operating on the ``FooBar`` project.

Running a command
=================

You run a command on a project by calling its ``dodo`` script with the name of the command:

.. code-block:: bash

    ~/projects/FooBar/dodo_commands/env/bin/dodo foo --bar

This will execute the following steps:

#. the ``dodo`` script will read the ``command_path`` (a list of directories with command scripts) from the project's configuration file (``~/projects/FooBar/dodo_commands/res/config.yaml``).

#. the foo.py script is found and run with the --bar option

#. the foo.py script can access the project's configuration and does some operation on the project (such as deleting all build results in ~/projects/FooBar/build/debug)

Activating a project
====================

The ``~/projects/FooBar/dodo_commands/env/bin/dodo`` script is part of a virtual python environment that was installed when we called ``dodo activate FooBar --create``. You can save some typing by first activating this python environment with:

.. code-block:: bash

    source ~/projects/FooBar/dodo_commands/env/bin/activate

Running ``dodo`` will now find the project-specific dodo script, rather than the "system" one. You can run commands against the activated project with:

.. code-block:: bash

    dodo foo --bar

The short-cut to activating the python environment is using:

.. code-block:: bash

    $(dodo activate FooBar)

If you omit the ``$()`` part then ``dodo activate`` prints the line ``source ~/projects/FooBar/dodo_commands/env/bin/activate``. The ``$(...)`` syntax takes care of executing this in the shell. To create a new project and activate it at the same time, call:

.. code-block:: bash

    $(dodo activate FooBar --create)

If you activated a project and you want to go back to the previously active project, run ``$(dodo activate -)``.

.. _autostart:

Activating the last used project
================================

You can activate the last used project with ``$(dodo activate --latest)``. To perform this action automatically when you open a terminal, you can call ``dodo autostart on``. This writes a small script file to ``~/.dodo_commands_autostart``.

.. code-block:: bash

    dodo autostart on
    cat ~/.dodo_commands_autostart

    > $(dodo activate --latest)
    > dodo check-config-version
    > dodo check-version

Then, add the following lines to your ``~/.bashrc`` to execute this script when a terminal is opened:

.. code-block:: bash

    if [ -f ~/.dodo_commands_autostart ]; then
        . ~/.dodo_commands_autostart
    fi

If you want to disable the autostart behaviour, call ``dodo autostart off``. This will delete the ``~/.dodo_commands_autostart`` file, and therefore disable the automatic project activation.
