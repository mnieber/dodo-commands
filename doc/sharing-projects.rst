.. _sharing_projects:

****************
Sharing projects
****************

Objectives
==========

If someone joins your project, then it makes sense to share your working environment with them. At the same time, you want working environments to be independent, so that each project member can arrange it to their preferences. This is achieved by having a shared configuration from which you cherry-pick the parts you need (this is somewhat comparable to how remote repositories work in git).

In the explanation below, we'll assume that you have the following project directory layout:

.. code-block:: bash

    ~/projects/FooBar                    # root of the project
    ~/projects/FooBar/src                # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/dodo_commands/res  # your Dodo Commands configuration files

Bootstrapping
=============

Let's assume that you wish to share your project with new team members. Follow these steps:

- copy your Dodo Commands configuration files to the location ``~/projects/FooBar/src/extra/dodo_commands/res`` and commit this to your git repository. These copies are the project's shared Dodo configuration. All team members (including you) will synchronize their local configuration file with this shared file.

- ask your colleague to create an empty Dodo Commands project using ``dodo activate FooBar --create``.

Your colleague then calls the ``bootstrap`` command to clone ``foobar.git`` and initialize their local Dodo Commands configuration with copies of the shared configuration files:

.. code-block:: bash

    dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/foo/foobar.git

In the above example, the repository is cloned to the ``src`` subdirectory of the project directory. The shared configuration files are copied from the ``extra/dodo_commands/res`` location (which is relative to ``src``) to ``~/projects/FooBar/dodo_commands/res``. Finally, the location of the cloned sources (``src``) is stored in the configuration under the ``${/ROOT/src_dir}`` key, and the location of the shared configuration files is stored under ``${/ROOT/shared_config_dir}``.

At this point, your colleague has the same directory structure as you:

.. code-block:: bash

    ~/projects/FooBar                                # root of the project
    ~/projects/FooBar/src                            # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/src/extra/dodo_commands/res    # default Dodo Commands configuration files
    ~/projects/FooBar/dodo_commands/res              # local copies of the default Dodo Commands configuration files

- the ``${/ROOT/shared_config_dir}`` directory is used by the ``dodo diff`` command to show the differences between your local configuration files and the shared files. If you are using the recommended diff tool (meld) then you will now be able to copy parts of your local configuration to the shared one. When you push these changes to version control, your colleages will later be able to incorporate your changes (also by copying parts) when they run ``dodo diff``.

- As mentioned, we recommend to set :code:`meld` as the ``diff_tool`` in :code:`~/.dodo_commands/config`:

.. code-block:: bash

    dodo global-config settings.diff_tool meld

- To synchronize only config.yaml, call ``dodo diff config.yaml``.

- It's a good practice to use the value ``${/ROOT/version}`` to track whether the copied configuration is up-to-date or not (see :ref:`check_config`).


.. _check_config:

Checking the config version
===========================

The ``dodo check-config --config`` command compares the ``${/ROOT/version}`` value in your local configuration with the value in the shared configuration. If someone bumped the version in the shared configuration, it will tell you that your local configuration is not up-to-date (in that case, use ``dodo diff`` to synchronize).
One of the synchronized values is ``${/ROOT/required_dodo_commands_version}``. The ``dodo check-version --dodo`` command reads this value and warns you if your Dodo Commands version is too old. The small script written by ``dodo autostart on`` (see :ref:`autostart`) calls both checks, and this helps you to stay synchronized.


Starting a project from a cookiecutter template
===============================================

It's convenient to start a brand new project from a cookiecutter template. This can be achieved by using the ``cookiecutter-url`` option instead of ``git-url`` in the ``bootstrap`` call:

.. code-block:: bash

    dodo bootstrap src extra/dodo_commands/res --force --cookiecutter-url https://github.com/foo/foobar.git

Note that the cookiecutter url can also point to a directory on the local filesystem.


Symlinking to a local src directory (useful with monolithic repositories)
=========================================================================

A monolithic repository may contain several projects that each have their own Dodo Commands configuration. In this scenario, each Dodo Commands project should use a symlink to a subdirectory of the monolithic source tree:

.. code-block:: bash

    # Get monolithic repository.

    cd ~/sources
    git clone https://github.com/foo/monolith.git

    $(dodo activate --create foobar)

    # Bootstrap the foobar project without cloning the sources, copying the
    # configuration from ~/sources/monolith/foobar/extra/dodo_commands/res
    dodo bootstrap --link-dir ~/sources/monolith/foobar extra/dodo_commands/res --force
