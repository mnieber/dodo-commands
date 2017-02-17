.. _sharing_projects:

****************
Sharing projects
****************

Sharing projects
================

If someone wants to join your project, then it makes sense to share your working environment with them. At the same time, you want your working environment to be independent, so that you can arrange it to your preferences.
In the explanation below, we'll assume that you have the following project directory layout:

.. code-block:: bash

    ~/projects/FooBar                    # root of the project
    ~/projects/FooBar/src                # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/dodo_commands/res  # your Dodo Commands configuration files

Bootstrapping
=============

The proposed solution to the above problem is the following:

- you add *default* Dodo Commands configuration files at
location :code:`~/projects/FooBar/src/extra/dodo_commands/res` and
commit this to your git repository.

- your colleague starts out by creating an empty Dodo Commands project using
:code:`dodo-activate FooBar --create`.

Your colleague then calls the :code:`bootstrap` command to clone the project repository
and (at the same time) initialize their Dodo Commands configuration with the
default configuration files:

.. code-block:: bash

    dodo bootstrap src extra/dodo_commands/res --force --git-url https://github.com/foo/foobar.git

Note that the path :code:`extra/dodo_commands/res` is relative to the root of the
cloned repository. At this point, your colleague has the same directory
structure as you, with one additional symlink:

.. code-block:: bash

    ~/projects/FooBar                                # root of the project
    ~/projects/FooBar/src                            # cloned https://github.com/foo/foobar.git repository
    ~/projects/FooBar/src/extra/dodo_commands/res    # default Dodo Commands configuration files
    ~/projects/FooBar/dodo_commands/res              # local copies of the default Dodo Commands configuration files
    ~/projects/FooBar/dodo_commands/default_project  # symlink to ~/projects/FooBar/src/extra/dodo_commands/res

- the additional symlink is used by the :code:`dodo diff` command to show the differences between your local configuration files and the default files. Your colleague can freely change their local configuration files and use `dodo diff .` to update the default files and push them.

- you can add the extra symlink to your project as well by calling :code:`dodo bootstrap` without the :code:`--git-url` argument:

.. code-block:: bash

    dodo bootstrap src extra/dodo_commands/res --force

- To synchronize only config.yaml, call :code:`dodo diff config.yaml`. It's a good practice to use the value ${/ROOT/version} to track whether the copied configuration is up-to-date or not.
