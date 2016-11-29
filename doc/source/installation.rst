.. _installation:

************
Installation
************

Step 1: Install prerequisites
==========================================

Dodo commands depends on the python-virtualenv package:

.. code-block:: bash

    sudo apt-get install python-virtualenv


Step 2: Clone and install
==========================================

The Dodo commands system will run directly from the folder in which it was cloned. To clone and install, run:

.. code-block:: bash

    git clone https://github.com/mnieber/dodo_commands
    source dodo_commands/bin/install.sh

The install script will print instructions on how to extend the path so that dodo-activate will be found when you call it.
After installing, there will be a new dodo_commands.config file that contains the path to the projects folder. This folder stores specific data for each project, such as the project configuration file.


Step 3: Install some default commands
=====================================

At this point, the Dodo commands framework is installed but it will not contain any commands you can run. To install the standard Dodo commands, run:

.. code-block:: bash

    dodo-install-defaults --ln --commands ./dodo_commands/extra/standard_commands
