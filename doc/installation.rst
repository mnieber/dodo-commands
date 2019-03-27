.. _installation:

************
Installation
************


Step 1: Install software
========================

Dodo Commands depends on the python-virtualenv package. In addition, some of the Dodo commands use git.

.. code-block:: bash

    # install prerequisites
    sudo apt-get install python-virtualenv git

    # install dodo commands
    sudo pip install dodo_commands

.. tip::

   On Mac you may need to create a file ``~/.distutils.cfg`` that `sets an empty prefix <http://stackoverflow.com/a/24357384/301034>`_ to prevent errors stating "must supply either home or prefix/exec-prefix -- not both".


Step 2: (Optional) Extend the path
==================================

.. note::

    This step is only necessary if you installed :code:`dodo_commands` into a virtual environment.

To make sure that the :code:`dodo` command is always found, call :code:`which dodo` and add the resulting path (the directory part) to the PATH in in your :code:`~/.bashrc`. The result should look something like this:

.. code-block:: bash

    export PATH=$PATH:/home/maarten/projects/dodo_commands_env/bin


Step 3: (Optional) Tweak global configuration
=============================================

The first time you call :code:`dodo`, a global :code:`~/.dodo_commands/config` file is created (unless it already exists) with the following settings:

- :code:`projects_dir` is the location where your projects are stored (defaults to :code:`~/projects`)

- :code:`python` is the python interpreter that is used in the virtualenv of your projects (defaults to :code:`python`). If your OS uses Python 2 by default then you may want to set this to :code:`python3` to use the latest python.

- :code:`diff_tool` is the diff tool used to show changes to your project configuration files. It's recommended to install and use :code:`meld` for this option:

.. code-block:: bash

    dodo global-config settings.diff_tool meld


Step 4: (Optional) Install extra default commands
=================================================

The :code:`dodo_standard_commands` directory is added by default to the ``~/.dodo_commands/default_commands`` directory where default commands are installed. To install additional commands into this directory, you can run

.. code-block:: bash

    dodo install-default-commands --pip dodo_webdev_commands --pip dodo_git_commands --pip dodo_deploy_commands


Step 5: (Optional) Enable autocompletion
========================================

The :code:`dodo register-autocomplete` command prints a line that - when executed - installs an autocompletion script in ``/etc/bash_completion.d``. You can paste this line into a bash-console, or run it directly with :code:`$(dodo register-autocomplete)`.

.. code-block:: bash

    # returns: sudo register-python-argcomplete dodo > /etc/bash_completion.d/dodo_autocomplete.sh
    dodo register-autocomplete


Step 6: (Optional) Activate the latest project automatically
============================================================

To automatically activate the last used Dodo Commands project, add this line to your :code:`~/.bashrc` file:

.. code-block:: bash

    $(dodo activate --latest)

If you wish to be able to toggle the automatic activation on and off, read about :ref:`autostart`.


Upgrading
=========

To upgrade Dodo Commands, you need to upgrade its pip package. If you have activated a Dodo Commands project with ``$(dodo activate foo)`` then the first step is to deactivate it by typing ``deactivate``. This is necessary because we don't want to use the ``pip`` from the virtual environment.

Now, to upgrade, simply run ``pip install --upgrade dodo_commands``. To upgrade a commands package (for example: dodo_git_commands), simply install it again using ``dodo install-default-commands --pip dodo_git_commands``.
