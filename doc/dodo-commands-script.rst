.. _dodo_commands_script:

************************************
The basics of a dodo commands script
************************************

In this section we'll explain how to run global commands, and discuss the basic outline of a Dodo Commands script. This should give you an idea of how to automate any task. Later we will expand on this information, and show how to organize your commands into different projects.


Global commands and the command path
====================================

The recommended way of using Dodo Commands is to create a Dodo Commands project and write a configuration file. However, it's possible to run commands without having any project. In this case, Dodo Commands will provide a fallback configuration that gives access to all commands in the global commands directory. If you inspect this fallback configuration by running ``dodo print-config``, you will see that it tells Dodo Commands which commands are available via the ``/ROOT/command_path`` setting. To list all available commands, simply run ``dodo``.


The hello-world command script
==============================

The example we will use is a ``hello-world.py`` script which parses some command line arguments and prints a text:

.. code-block:: python

    # hello-world.py

    from argparse import ArgumentParser

    from dodo_commands.framework import Dodo

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

In later sections, we will explain how to extend the command path so that you will be able to run it with ``dodo hello-world``.


Explanation
===========

The lines that require special attention are numbered with a comment:

1. We use ``Dodo.parse_args(parser)`` instead of ``parser.parse_args()`` to give Dodo Commands the chance to add some extra arguments to your script, such as the ``--confirm`` flag (which is explained below).

2. Through the ``Dodo`` singleton, every command has access to the configuration values of the current project. The value 'no project' is a fallback in case there is no current project.

3. This line is a variation on the usual ``if __name__ == '__main__'``. It allows you to execute the script when invoking it with ``dodo hello-world``.

4. The purpose of ``Dodo.run`` is to execute a command while giving Dodo Commands a chance to intercept the call and do something different. Important use cases are the ``--confirm`` flag (which will ask for confirmation before proceeding) and the ``--echo`` flag (which will print the command without doing anything). Note:

- if you use the ``--confirm`` flag twice then also nested ``dodo`` calls (i.e. any calls to ``dodo`` that are executed inside the Dodo Command script) will ask for confirmation.

- it's encouraged to make your Dodo Commands script act like a shell alias. When users see the script as a way to avoid typing, rather than as a magical invocation, they are more likely to use it.


Using pipes and redirection
===========================

Since pipes and redirection are handled by the shell, you need to explicitly mention the shell executable to use them, e.g.

.. code-block:: python

    if Dodo.is_main(__name__):
        args = _args()
        Dodo.run(['/bin/bash', '-c', 'echo \'Hello world\' > /tmp.out'])

You can shorten this a little using the ``bash_cmd`` helper function:

.. code-block:: python
    from dodo_commands.framework.util import bash_cmd

    if Dodo.is_main(__name__):
        args = _args()
        Dodo.run(bash_cmd('echo \'Hello world\' > /tmp.out'))
