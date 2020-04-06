.. _installation:

************
Installation
************


Step 1: Install Dodo Commands
=============================


.. code-block:: bash

    # install dodo commands
    sudo pip install dodo_commands

.. tip::

   On Mac you may need to create a file ``~/.distutils.cfg`` that `sets an empty prefix <http://stackoverflow.com/a/24357384/301034>`_ to prevent errors stating "must supply either home or prefix/exec-prefix -- not both".


Step 2: (Optional) Install virtualenv and git
=============================================

Some commands depend on the python-virtualenv package. In addition, some of the Dodo commands use git.

.. code-block:: bash

    # install prerequisites
    sudo apt-get install python-virtualenv git


Step 3: (Optional) Activate the latest project automatically
============================================================

To automatically activate the last used Dodo Commands project, call ``dodo autostart on``. This writes a small ``dodo_autostart`` shell script into ``~/.config/fish/conf.d`` and ``~/.config/bash/conf.d``. Call ``dodo autostart off`` to turn automatic activation off, this will delete the ``dodo_autostart`` script. The Fish shell will automatically find the ``dodo_autostart`` script and run it when the shell starts. To have the same behaviour in Bash, add this line to your ``~/.bashrc`` file:

.. code-block:: bash

    if [ -f ~/.config/bash/conf.d/dodo_autostart ]; then
        . ~/.config/bash/conf.d/dodo_autostart
    fi

.. code-block:: bash
