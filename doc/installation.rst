.. _installation:

************
Installation
************

Step 1: Install prerequisites
==========================================

Dodo Commands depends on the python-virtualenv package, and you will need git to clone the source files:

.. code-block:: bash

    sudo apt-get install python-virtualenv git


Step 2: Clone and install
==========================================

The Dodo Commands system will run directly from the directory in which it was cloned. To clone and install, run:

.. code-block:: bash

    git clone https://github.com/mnieber/dodo_commands
    source dodo_commands/bin/install.sh

The install script will print instructions on how to extend the path so that :code:`dodo-activate` will be found when you call it. After installing, there will be a new dodo_commands.config file that contains the path to the projects directory. This directory stores specific data for each project, such as the project configuration file.

The install script takes the following optional arguments:

- :code:`projects_dir` is the location where your projects are stored (defaults to :code:`~/projects`)

- :code:`python` is the python interpreter that is used in the virtualenv of your projects (defaults to :code:`python`). If your OS uses Python 2 by default then you may want to set this to :code:`python3` to use the latest python.

Step 3: Install some default commands
=====================================

At this point, the Dodo Commands framework is installed but it will not contain any commands you can run. To install the standard Dodo Commands, run:

.. code-block:: bash

    dodo-install-defaults --ln --commands ./dodo_commands/extra/standard_commands
