************************************************
Scenario: using project-specific sets of aliases
************************************************

We will again continue where we left off in part 2. This time we will create a new Dodo Commands
environment, and show how to reuse one of the scripts that we created before.
If you haven't done the steps of the previous scenario, run these steps to get started:

.. code-block:: bash

  cd /tmp
  git clone git@github.com:mnieber/dodo_commands_tutorial.git

  # Copy the end state of part 2 of the tutorial
  cp -rf ./dodo_commands_tutorial/part2/after ./dodo_tutorial

  # Create and activate a dodo environment for our project
  cd ./dodo_tutorial
  $(dodo env --init dodo_tutorial)


Activating the default Dodo Commands environment
================================================

Let's start by deactivating the current ``dodo_tutorial`` environment. You do this by activating
the default environment:

.. code-block:: bash

  # activate default environment
  $(dodo env default)

  dodo which

      default

The default environment is similar to all other environment. Let's check it out:

.. code-block:: bash

  # Print the Dodo Commands environment directory
  dodo which --env-dir

      ~/.dodo_commands/envs/default

  # Print the project directory
  dodo which --project-dir

      ~/.dodo_commands/default_project

  # Print the configuration
  dodo print-config

      ROOT:
        env_name: default
        version: 1.0.0
        config_dir: ~/.dodo_commands/default_project
        command_path:
        - ~/.dodo_commands/default_project/commands/*
        - /home/dodo/projects/dodo_commands/dodo_commands/dodo_system_commands
        project_dir: ~/.dodo_commands/default_project


Creating a new environment
==========================

Let's start by deactivating the current ``dodo_tutorial`` environment. You do this by activating
the default environment:

.. code-block:: bash

  # activate default environment
  $(dodo env default)

  dodo which

      default

Now we'll create a new project in the ``~/projects`` directory. The new project will have
a python virtual environment:

.. code-block:: bash

  # create a new project with python virtual environment
  $(dodo env --create --create-virtual-env foo)

      Creating project directory ~/projects/foo ... done

  # check that we've switched to the foo environment
  dodo which

      foo

  # check that we're using the new python virtual environment
  which python

      ~/projects/foo/.env/bin/python

.. tip::

  You can change the standard location for creating new projects in the
  ``~/.dodo_commands/config`` file. You can edit this file or call

  .. code-block:: bash

    dodo global-config settings.projects_dir /path/to/projects


Using environments directly
===========================

If we want to use the previous ``dodo_tutorial`` environment, then we can activate it with
``$(dodo env -)``. However, we can also use it directly with
``~/.dodo_commands/bin/dodo-dodo_tutorial``. It's a good idea to add ``~/.dodo_commands/bin/`` to the
system path to make this easier:


.. code-block:: bash

  # extend the path
  export PATH=$PATH:~/.dodo_commands/bin

  # call the dodo entry point in the dodo_tutorial environment
  dodo-dodo_tutorial which

      dodo_tutorial

  # call the dodo entry point in the foo environment
  dodo-foo which

      foo


Installing more commands
========================

By default, our new environment is using all command directories in ``~/.dodo_commands/default_project/commands/*``.
To install more commands, use ``dodo install-commands``:

.. code-block:: bash

  # Activate the default environment first, otherwise Dodo will complain
  $(dodo env default)

  # Install the dodo_git_commands pip package
  dodo install-commands --pip dodo_git_commands --to-defaults --confirm

      (/) python3.5 -m pip install --upgrade --target ~/.dodo_commands/commands dodo_git_commands

      confirm? [Y/n]

      Collecting dodo_git_commands
      Successfully installed dodo-git-commands-0.3.0

      (/) ln -s ~/.dodo_commands/commands/dodo_git_commands ~/.dodo_commands/default_project/commands/dodo_git_commands

      confirm? [Y/n]

We see that the commands are installed into the ~/.dodo_commands/commands directory. Because we passed the ``to-default``
flag, a symlink to dodo_git_commands is created in ~/.dodo_commands/default_project/commands. Because our project uses
all the default commands, the new git commands will be available:

.. code-block:: bash

  # Print the command path
  dodo pc /ROOT/command_path

      - ~/.dodo_commands/default_project/commands/*
      - /some/path/to/dodo_commands/dodo_commands/dodo_system_commands

  dodo which git-multi-status

      ~/.dodo_commands/commands/dodo_git_commands/git-multi-status.py

