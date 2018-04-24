.. _singleton:

******************
The Dodo singleton
******************

This chapter describes the functions offered by the Dodo singleton class. You can use these functions in any Dodo Command script.


The is_main function
====================

Using ``if Dodo.is_main(__name__)`` instead of the usual ``if __name__ == '__main__'`` allows Dodo Commands to execute your script also when its invoked through calling ``dodo``.


.. code-block:: python

    from dodo_commands.framework import Dodo

    if Dodo.is_main(__name__):
        print("Hello world")


The get_config function
=======================

Calling ``Dodo.get_config('/ROOT/my/key', 'default-value')`` will retrieve a value from the project's :ref:`configuration`. Use ``Dodo.config`` to get direct access to the configuration object.


The runcmd function
===================

The ``Dodo.runcmd`` function takes a list of arguments (and a current working directory) and runs them on the command line. Moreover, it adds all variables in ``${/ENVIRONMENT/variable_map}`` to the system environment (for the duration of running the command).

.. code-block:: python

    if Dodo.is_main(__name__):
        # You must call Dodo.parse_args before calling Dodo.runcmd,
        # or an exception will be raised
        parser = ArgumentParser()
        parser.add_argument(
            '--verbose',
            action="store_true",
        )
        args = Dodo.parse_args(parser)

        # say hello
        if args.verbose:
            Dodo.runcmd(['echo', 'hello'], cwd='/tmp')


The --confirm and --echo flags
==============================

The ``Dodo.parse_args(parser)`` function adds an ``--echo`` and ``--confirm`` flag the to command line arguments of your script. These flags control what happens in the ``Dodo.runcmd`` function:

#. the :code:`--echo` flag changes the behaviour of :code:`runcmd` so that it only prints a command line instead of executing the command.

#. the :code:`--confirm` flag changes the behaviour of :code:`runcmd` so that it prints a command line and asks for confirmation before executing the command.


Marking a script as unsafe
==========================

Since command scripts are written in Python, the script can in principle perform any operation without explicitly asking your permission. In other words, it may choose to ignore the --confirm and --echo options. This sitation should of course be avoided. However, if a Command script does not completely honor the ``--confirm`` and ``--echo`` flags, it should pass ``safe=False`` when it calls ``Dodo.is_main``, as shown in the example below. Unsafe commands will not run with the --echo flag, and will pause with a warning when run with the --confirm flag.

.. code-block:: python

    if Dodo.is_main(__name__, safe=False):
        parser = ArgumentParser()
        args = Dodo.parse_args(parser)

        # Do destructive things without asking permission. Having this call
        # is the reason we used safe=False to mark the script as unsafe.
        os.unlink('/tmp/foo.text')

        # Delete the /tmp directory. Since this time we are using Dodo.runcmd,
        # the user can use the --confirm flag to inspect and cancel it.
        # This makes this call *relatively* safe.
        Dodo.runcmd(['rm', '-rf', '/tmp'])


.. _decorators:

Decorators
==========

A Decorator is a class that alters the workings of a Dodo Command script. It can extend or modify the arguments that are passed to ``Dodo.runcmd``. The decorator should be placed in a ``decorators`` directory inside a commands directory. This is illustrated by the following example:

.. code-block:: python

    # file: my_commands/decorators/debugger.py

    class Decorator:  # noqa
        def add_arguments(self, parser):  # noqa
            parser.add_argument(
                '--use-debugger',
                action='store_true',
                default=False,
                help="Run the command through the debugger"
            )

        def modify_args(self, root_node, cwd):  # noqa
            if not Dodo.args.use_debugger:
                return root_node, cwd

            # Create a command argument with the path to the debugger
            # Note that "debugger" is a tag which is only used internally
            debugger_node = ArgsTreeNode(
                "debugger", args=[Dodo.get_config('/BUILD/debugger')]
            )

            # create a new command by using debugger_node as a prefix, and
            # adding the existing root_node command as a postfix
            debugger_node.add_child(root_node)
            return debugger_node, cwd


Note that not all decorators are compatible with all commands. For example, only some commands can be run inside a debugger. Therefore, for each decorator you should list in the configuration which commands are decorated. When listing the commands, wildcards are allowed, and you can exclude commands by prefixing them with an exclamation mark:

.. code-block:: yaml

    ROOT:
      decorators:
        # Use a wildcard to decorate all commands, but exclude the foo command
        debugger: ['*', '!foo']
        # cmake and runserver can be run inside docker
        docker: ['cmake', 'runserver']
