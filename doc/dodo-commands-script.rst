.. _dodo_commands_script:

************************************
The basics of a dodo commands script
************************************

We're going to jump ahead a bit and talk first about the basic outline of a Dodo Commands script. Later we will expand on this information, and show how to organize your commands into different projects.


The hello-world command script
==============================

The example we will use is a ``hello-world.py`` script which parses some command line arguments and prints a text:

.. code-block:: python

    # hello-world.py

    from argparse import ArgumentParser
    import sys

    try:
        from dodo_commands.framework import Dodo
    except ImportError:
        print("This script requires that dodo_commands is installed")
        sys.exit(1)

    def _args():  # noqa
        parser = ArgumentParser(description=('Print hello world.'))
        args = Dodo.parse_args(parser)  # 1
        args.project_name = Dodo.get_config('/ROOT/project_name', 'no project')  # 2
        return args

    if Dodo.is_main(__name__):  # 3
        args = _args()
        Dodo.run(['echo', 'Hello world']) # 4


Assuming that ``dodo_commands`` is installed, you can run this simply as a Python script:

.. code-block:: python

    python hello-world.py

Later, we will see how to set up a Dodo Commands project so that you can also run the command with `dodo hello-world`.


Explanation
===========

The lines that require special attention are numbered with a comment:

1. We use ``Dodo.parse_args(parser)`` instead of ``parser.parse_args()`` to give Dodo Commands the chance to add some extra arguments to your script, such as the ``--confirm`` flag (which is explained below).

2. Through the ``Dodo`` singleton, every command has access to the configuration values of the current project. By default, the project name is made available in this configuration. We also provide a fallback value ('no project') in case there is no current project.

3. Calling ``dodo hello-world`` makes Dodo Commands import your script. But just importing the script is not enough: we want to run it. This is achieved by using ``if Dodo.is_main(__name__)`` instead of the usual ``if __name__ == '__main__'``.

4. In most cases you should aim to make your Dodo Commands script act like a shell alias. When users see the script as a way to avoid typing, rather than as a magical invocation, they are more likely to use it. This is achieved by forwarding all the real work to the ``Dodo.run`` function, which will execute commands on the shell, and allow the user to intercept them through the ``--confirm`` flag (which will ask for confirmation before proceeding) or through the ``--echo`` flag (which will print the command without doing anything).
