.. _installation:

Installation
============


Step 1: Install Dodo Commands
-----------------------------


.. code-block:: bash

    # install dodo commands
    sudo pip install dodo_commands

.. tip::

   On Mac you may need to create a file ``~/.distutils.cfg`` that `sets an empty prefix <http://stackoverflow.com/a/24357384/301034>`_ to prevent errors stating "must supply either home or prefix/exec-prefix -- not both".

.. tip::

   Autocompletion is provided for bash, fish and zsh (you need to restart the shell after installation).
   For activating autocompletion in zsh you need to add the code below to .zshrc.

.. code-block:: bash

    autoload bashcompinit
    bashcompinit
    eval "$(register-python-argcomplete dodo)"


Step 2: (Optional) Install virtualenv and git
---------------------------------------------

Some commands depend on the python-virtualenv package. In addition, some of the Dodo commands use git.

.. code-block:: bash

    # install prerequisites
    sudo apt-get install python-virtualenv git


Step 3: (Optional) Activate the latest project automatically
------------------------------------------------------------

To automatically activate the last used Dodo Commands project, call ``dodo autostart on``.
This creates a ``~/.config/fish/conf.d/dodo_autostart.fish`` and a ``~/.config/bash/conf.d/dodo_autostart.bash`` script.
Call ``dodo autostart off`` to turn automatic activation off, this will delete the ``dodo_autostart`` script.
The Fish shell will automatically find the ``dodo_autostart.fish`` script and run it when the shell starts.
To have the same behaviour in Bash, add this line to your ``~/.bashrc`` file:

.. code-block:: bash

    if [ -f ~/.config/bash/conf.d/dodo_autostart.bash ]; then
        . ~/.config/bash/conf.d/dodo_autostart.bash
    fi


Step 4: (Optional) Add fish shell key-bindings for the dial command
-------------------------------------------------------------------

If you are using the fish shell then it's highly recommended to add the
key-bindings for the (:ref:`dial`) command (click the link for instructions).
These key-binding allow you to change the current directory to one of the
preset directories (that are configured in the project configuration file),
which can really speed up your work-flow in the terminal.