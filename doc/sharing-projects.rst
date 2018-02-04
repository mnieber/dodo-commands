.. _sharing_projects:

****************
Sharing projects
****************

Objectives
==========

If someone joins your project, then it makes sense to share your working environment with them. At the same time, you want working environments to be independent, so that each project member can arrange it to their preferences. How this is achieved should become clear in this chapter.

In the explanation below, we'll assume that you have the following project directory layout:

.. code-block:: bash

    ~/projects/FooBar                    # root of the project
    ~/projects/FooBar/src                # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/dodo_commands/res  # your Dodo Commands configuration files

Bootstrapping
=============

To share your project with new members, follow these steps:

- copy your Dodo Commands configuration files to the location ``~/projects/FooBar/src/extra/dodo_commands/res`` and commit this to your git repository. These copies are the project's default Dodo configuration.

- your colleague starts out by creating an empty Dodo Commands project using ``dodo activate FooBar --create``.

Your colleague then calls the ``bootstrap`` command to clone the project repository and initialize their Dodo Commands configuration with the default configuration files:

.. code-block:: bash

    dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/foo/foobar.git

In the above example, the repository is cloned to the ``src`` subdirectory of the project directory. The default configuration files are copied from the ``extra/dodo_commands/res`` location (which is relative to the root of the cloned repository) to ``~/projects/FooBar/dodo_commands/res``. Finally, the location of the cloned sources (``src``) is stored in the configuration under the ``${/ROOT/src_dir}`` key.

At this point, your colleague has the same directory structure as you, with one additional symlink:

.. code-block:: bash

    ~/projects/FooBar                                # root of the project
    ~/projects/FooBar/src                            # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/src/extra/dodo_commands/res    # default Dodo Commands configuration files
    ~/projects/FooBar/dodo_commands/res              # local copies of the default Dodo Commands configuration files
    ~/projects/FooBar/dodo_commands/default_project  # symlink to ~/projects/FooBar/src/extra/dodo_commands/res

- the additional symlink is used by the ``dodo diff`` command to show the differences between your local configuration files and the default files. Your colleague can freely change their local configuration files and use `dodo diff .` to update the default files and push them.

You (as the initial creator of the project) don't have this symlink, but you can create it manually with the ``ln -s <from> <to>`` command. Then, call ``dodo diff`` to test if you have set it up correctly.

- we recommend to set :code:`meld` as the ``diff_tool`` in :code:`~/.dodo_commands/config`:

.. code-block:: bash

    dodo global-config diff_tool meld

- To synchronize only config.yaml, call ``dodo diff config.yaml``. It's a good practice to use the value ``${/ROOT/version}`` to track whether the copied configuration is up-to-date or not (see :ref:`check_config`).


Starting a project from a cookiecutter template
===============================================

It's convenient to start a new project from a cookiecutter template. This can be achieved by using the ``cookiecutter-url`` option instead of ``git-url`` in the ``bootstrap`` call:

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

.. _check_config:

Checking the config version
===========================

The ``dodo check-config --config`` command compares the ``${/ROOT/version}`` value in your local configuration with the value in the (shared) default configuration. If someone bumped the version in the shared configuration, it will tell you that your local configuration is not up-to-date (in that case, use ``dodo diff .`` to synchronize).
One of the values that you synchronize with ``dodo diff .`` is ``${/ROOT/required_dodo_commands_version}``. The ``dodo check-version --dodo`` command reads this value and warns you if your Dodo Commands version is too old (if it is, then you can run ``dodo upgrade`` to upgrade Dodo Commands). The small script written by ``dodo autostart on`` (see :ref:`autostart`) calls both checks, and this helps you to stay synchronized.
