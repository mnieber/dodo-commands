.. _how-it-works:

**********************************
How the Dodo Commands system works
**********************************

After following the :ref:`installation` steps, you can create new projects in the projects directory and work with them. We'll explain how it works the long and clunky way, and then how the same can be done faster.

Creating a project
==================

Projects are created with the dodo-activate command::

    dodo-activate FooBar --create

Running this command creates a new FooBar project directory with various files. The most important one is the :code:`~/projects/FooBar/dodo_commands/env/bin/dodo` script file. Any further operation on the project is performed by calling this script with the appropriate options.

Running a command
=================

You run a command on a project by calling its :code:`dodo` script with the name of the command:

~/projects/FooBar/dodo_commands/env/bin/dodo foo --bar

This call will execute the following steps:

#. the dodo script will load the :code:`command_path` (a list of directories with command scripts) from the project's configuration file (:code:`~/projects/FooBar/dodo_commands/res/config.yaml`).

#. the foo.py script is found and run with the --bar option
@maarten what happens with lines in between?

#. the foo.py script will import several python modules from :code:`~/projects/FooBar/dodo_commands/framework` (this is a symlink to the framework directory of the Dodo Commands package)

#. the foo.py script reads the project configuration and does some operation on the project (such as deleting all build results in ~/projects/FooBar/build/debug)

Activating a project
====================

The :code:`~/projects/FooBar/dodo_commands/env/bin/dodo` script is part of a virtual python environment that was installed when we called :code:`dodo-activate FooBar --create`. You can save some typing by first activating this python environment with:

.. code-block:: bash

    source ~/projects/FooBar/dodo_commands/env/bin/activate

and then running any further commands with:

.. code-block:: bash

    dodo foo --bar

The short-cut to activating the python environment is using:

.. code-block:: bash

    $(dodo-activate FooBar)

The way this works is that the dodo-activate command prints the line :code:`source ~/projects/FooBar/dodo_commands/env/bin/activate` to the console, and the :code:`$(...)` syntax takes care of executing this in the shell. To create a new project and activate it at the same time, call:

.. code-block:: bash

    $(dodo-activate FooBar --create)

Adding dodo-activate to .bashrc
===============================

It's convenient to automatically activate the last used dodo commands project
when you open a new shell. This can be achieved by adding

.. code-block:: bash

    $(dodo-activate --latest)

to your `.bashrc`.
