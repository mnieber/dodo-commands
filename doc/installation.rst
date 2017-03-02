.. _installation:

************
Installation
************

Step 1: Install prerequisites
==========================================

Dodo Commands depends on the python-virtualenv package.
In addition, some of the Dodo commands use git.

.. code-block:: bash

    sudo apt-get install python-virtualenv git


Step 2: Install
===============

.. code-block:: bash

    pip install dodo_commands


Step 3: Install some default commands
=====================================

At this point, the Dodo Commands framework is installed but it will not contain any commands you can run. To install the standard Dodo Commands, run:

.. code-block:: bash

    dodo-install-default-commands standard_commands

The :code:`standard_commands` directory was found "magically"
because it comes with the Dodo Commands python package.
To read more about installing default commands, see :ref:`commands`.


Step 4: (Optional) Create aliases
=================================

NOTE: this step is only necessary if you installed :code:`dodo_commands`
into a virtual environment.

To make sure that the :code:`dodo-activate` command is always found,
call :code:`which dodo-activate` and add an alias for the resulting path
in your :code:`~/.bashrc`. Do the same for the :code:`dodo-install-default-commands`
command. The result could look like this:

.. code-block:: bash

    alias dodo-activate=/home/maarten/projects/dodo_commands_env/bin/dodo-activate
    alias dodo-install-default-commands=/home/maarten/projects/dodo_commands_env/bin/dodo-install-default-commands


Step 5: (Optional) Activate the latest project automatically
============================================================

To automatically activate the last used Dodo Commands project, add this line to your :code:`~/.bashrc` file:

.. code-block:: bash

    $(dodo-activate --latest)


Step 6: (Optional) Tweak global configuration
=============================================

Calling :code:`dodo-activate --help` will create a global Dodo Commands settings file at location :code:`~/.dodo_commands/config` (unless it already exists):

- :code:`projects_dir` is the location where your projects are stored (defaults to :code:`~/projects`)

- :code:`python` is the python interpreter that is used in the virtualenv of your projects (defaults to :code:`python`). If your OS uses Python 2 by default then you may want to set this to :code:`python3` to use the latest python.

- :code:`diff_tool` is the diff tool used to show changes to your project configuration files. It's recommended to install and use :code:`meld` for this option.
