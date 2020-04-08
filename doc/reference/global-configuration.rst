********************
Global configuration
********************

The global configuration is stored in ``~/.dodo_commands/config``.

The settings section
====================

.. code-block:: ini

    [settings]
    # the location where your projects are stored (defaults to ~/projects)
    project_dir = ~/projects

    # the python interpreter that is used
    # a) in virtual environments created by Dodo Commands and
    # b) to install new Dodo Commands pip packages into the commands directory
    python = python3.5

    # the diff tool used to show changes to your project configuration files.
    # It's recommended to install and use ``meld`` for this option.
    diff_tool = meld


The alias section
=================

This section contains aliases for any dodo command, e.g.

.. code-block:: ini

    [alias]
    wh = which
    whpp = which --projects
