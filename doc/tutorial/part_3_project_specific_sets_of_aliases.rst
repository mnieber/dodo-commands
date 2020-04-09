.. _tutorial_part3:

Scenario: using project-specific sets of aliases
================================================

We will again continue where we left off in part 2 (:ref:`tutorial_part2`). This time we will create a
new Dodo Commands environment, and show how to reuse the ``/tpm/tutorial/commands`` directory that we
created. If you haven't done the steps of the previous scenario, run these steps to get started:

.. code-block:: bash

  cd /tmp
  git clone git@github.com:mnieber/dodo_commands_tutorial.git

  # Copy the end state of part 2 of the tutorial
  cp -rf ./dodo_commands_tutorial/part2/after ./tutorial

  # Create and activate a dodo environment for our project
  cd ./tutorial
  $(dodo env --init tutorial)


Activating the default Dodo Commands environment
------------------------------------------------

Let's start by deactivating the current ``tutorial`` environment. You do this by activating
the ``default`` environment:

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
        - /some/path/to/dodo_commands/dodo_system_commands
        project_dir: ~/.dodo_commands/default_project


Installing more commands
------------------------

By default, our new environment is using all command directories in ``~/.dodo_commands/default_project/commands/*``.
To install more commands there, use ``dodo install-commands``:

.. code-block:: bash

  # Activate the default environment first, otherwise Dodo will complain
  $(dodo env default)

  # Install the dodo_git_commands pip package
  dodo install-commands --pip dodo_git_commands --to-defaults --confirm

      (/) python3.5 -m pip install --upgrade --target ~/.dodo_commands/commands dodo_git_commands

      confirm? [Y/n]

      Collecting dodo_git_commands
      Successfully installed dodo-git-commands-0.3.0

      (/) ln -s \
        ~/.dodo_commands/commands/dodo_git_commands \
        ~/.dodo_commands/default_project/commands/dodo_git_commands

      confirm? [Y/n]

We see that the commands are installed into the ``~/.dodo_commands/commands`` directory.
Because we passed the ``to-default`` flag, a symlink to dodo_git_commands is created in
``~/.dodo_commands/default_project/commands``. Since our project uses all the default commands,
the new git commands will be available:

.. code-block:: bash

  # Print the command path
  dodo print-config /ROOT/command_path

      - ~/.dodo_commands/default_project/commands/*
      - /some/path/to/dodo_commands/dodo_system_commands

  dodo which git-multi-status

      ~/.dodo_commands/commands/dodo_git_commands/git-multi-status.py


Creating a new environment
--------------------------

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
---------------------------

In some cases we may want to call a command in a different environment without switching
to that environment. For example, we may only want to print its configuration. We can
do this by calling its entry-point in ``~/.dodo_commands/bin``:

.. code-block:: bash

  # Directly call the entry point of the tutorial environment
  ~/.dodo_commands/bin/dodo-tutorial which

      tutorial

  # We can extend the path to make this easier
  export PATH=$PATH:~/.dodo_commands/bin

  # Directly call the dodo entry point in the foo environment
  dodo-tutorial which

      tutorial


Using the mk.py script in the new environment
---------------------------------------------

To use the ``mk`` command script that we created in the ``tutorial`` environment, we need to have
``/tmp/tutorial/commands`` in our command_path. Surely, we can simply add this path to
``${/ROOT/command_path}``. The problem with this approach is that we may move the
``tutorial`` project to a new location, and then the hard-coded path will no longer
be correct. A better option is to install ``/tmp/tutorial/commands``
in the global commands directory, and then reference that location. Since the directory name ``commands`` is not
very descriptive, we will use the ``--as`` option to rename it to ``dodo_tutorial_commands``:

.. code-block:: bash

  dodo install-commands /tmp/tutorial/commands --as dodo_tutorial_commands --confirm

      (/tmp) ln -s \
        /tmp/tutorial/commands \
        ~/.dodo_commands/commands/dodo_tutorial_commands

      confirm? [Y/n]

Now, if we add ``~/.dodo_commands/commands/dodo_tutorial_commands`` to ``${/ROOT/command_path}`` then the ``mk``
command will be found:

.. code-block:: yaml

  ROOT:
    # other stuff
    command_path:
    - ~/.dodo_commands/default_project/commands/*
    - ~/.dodo_commands/commands/dodo_tutorial_commands


Before we can successfully call ``mk``, we should add a ``MAKE`` section to ``config.yaml``,
otherwise the command will fail:

.. code-block:: yaml

  # ~/projects/foo/.dodo_commands/config.yaml
  MAKE:
    cwd: /tmp


Importing symbols from a command script
---------------------------------------

So far, we've kept our ``mk`` script deliberately very simple. Let's refactor it by extracting a function
for running ``make``. We can then use this function in our ``mk-greet`` script. Change the ``mk.py``
script so it looks like this:

.. code-block:: python

  # /tmp/tutorial/commands/mk.py

  from dodo_commands import Dodo

  def run_make(*what):
      Dodo.run(["make", *what], cwd=Dodo.get("/MAKE/cwd"))

  if Dodo.is_main(__name__):
      Dodo.parser.add_argument("what")
      run_make(Dodo.args.what)

We can now use the ``run_make`` function in ``mk-greet.py``:

.. code-block:: python

  # /tmp/tutorial/commands/mk-greet.py

  from dodo_commands import Dodo
  from dodo_tutorial_commands.mk import run_make

  Dodo.parser.add_argument("greeting")
  run_make("greeting", "GREETING=%s" % Dodo.args.greeting)

.. note::

  The import of ``run_make`` from the ``dodo_tutorial_commands`` package succeeded because all
  packages in the ``${/ROOT/command_path}`` are added to ``sys.path`` during execution of the
  command.

.. note::

  You see that we added a line that says ``if Dodo.is_main(__name__)``. This replaces the standard line
  ``if __name__ == "__main__"`` which doesn't work when executing the script with ``dodo mk``. The reason
  is that ``dodo`` will import the ``mk.py`` script, which means that   ``mk.py`` is not the main module.

.. note::

  If the caller of the script uses the ``-confirm`` flag then they expect to be notified of any
  action before it's taken. If your script violates this assumption, then you should use
  ``Dodo.is_main(__name__, safe=False)``. This has the effect that the script will not run in combination
  with ``--confirm`` (instead, it will stop with an error message).


Specifying command dependencies in the .meta file
-------------------------------------------------

Each Dodo command should ideally run out-of-the-box. If the ``mk`` command needs additional Python packages,
you can describe them in a ``mk.meta`` file:

.. code-block:: yaml

  # /tmp/tutorial/commands/mk.meta
  requirements:
  - dominate==2.2.0

We can try this out by importing ``dominate`` in ``mk.py``:

.. code-block:: python

  # /tmp/tutorial/commands/mk.py

  import dominate
  from dodo_commands import Dodo

  # ... rest of the script stays the same

Calling the ``mk`` command will ask the user for confirmation to install the ``dominate``
package into the current Python environment:

.. code-block:: bash

  dodo mk runserver --confirm

      This command wants to install dominate==2.2.0:

      Install (yes), or abort (no)? [Y/n]

      Collecting dominate==2.2.0
      Successfully installed dominate-2.2.0
      --- Done ---

      (/tmp) make runserver

      confirm? [Y/n]
