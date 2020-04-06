The first time you call :code:`dodo`, a global :code:`~/.dodo_commands/config` file is created (unless it already exists) with the following settings:

- :code:`projects_dir` is the location where your projects are stored (defaults to :code:`~/projects`)

- :code:`python` is the python interpreter that is used in the virtualenv of your projects (defaults to :code:`python`). If your OS uses Python 2 by default then you may want to set this to :code:`python3` to use the latest python.

- :code:`diff_tool` is the diff tool used to show changes to your project configuration files. It's recommended to install and use :code:`meld` for this option:

.. code-block:: bash

    dodo global-config settings.diff_tool meld

