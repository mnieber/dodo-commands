*********************
The DodoCommand class
*********************

The :code:`BaseCommand` class is pretty simple: it offers a command line parser and access to the project configuration. The :code:`DodoCommand` class extends BaseCommand with advanced features.


The runcmd function, and --confirm and --echo flags
===================================================

The :code:`DodoCommand` class adds a helper function :code:`runcmd` and two additional flags:

#. the ``runcmd`` function takes a list of arguments and runs them on the command line. Moreover, it adds all variables in ``${/ENVIRONMENT/variable_map}`` to the system environment (for the duration of running the command).

#. the :code:`--echo` flag changes the behaviour of :code:`runcmd` so that it only prints a command line instead of executing the command.

#. the :code:`--confirm` flag changes the behaviour of :code:`runcmd` so that it prints a command line and asks for confirmation before executing the command.

Because the ``DodoCommand`` class implements :code:`add_arguments` and :code:`handle`, subclasses of ``DodoCommand`` must implement :code:`add_arguments_imp` and :code:`handle_imp` if they wish to customize the commands' argument or ``handle`` function.

Note that since command scripts are written in Python, the script may choose to perform any operation without explicitly asking your permission. In other words, it may choose to ignore the --confirm and --echo options. This sitation should of course be avoided. However, if a Command script does not completely honor the ``--confirm`` and ``--echo`` flags, it should be marked with ``safe = False``, as shown in the example below. Unsafe commands will not run with the --echo flag, and will pause with a warning when run with the --confirm flag.

.. code-block:: python

    class Command(DodoCommand):  # noqa
        safe = False

        # rest of the command goes here...


.. _decorators:

Decorators
==========

A Decorator is a class that alters the workings of a DodoCommand class. It can extend or modify the arguments that are passed to ``DodoCommand.handle``. The decorator should be placed in a ``decorators`` directory inside a commands directory. This is illustrated by the following example (note that the decorated DodoCommand instance is passed in as the ``decorated`` argument):

.. code-block:: python

    # file: my_commands/decorators/debugger.py

    class Decorator:  # noqa
        def add_arguments(self, decorated, parser):  # noqa
            parser.add_argument(
                '--use-debugger',
                action='store_true',
                default=False,
                help="Run the command through the debugger"
            )

        def handle(self, decorated, use_debugger, **kwargs):  # noqa
            decorated.opt_use_debugger = use_debugger


        def modify_args(self, decorated, root_node, cwd):  # noqa
            if not decorated.opt_use_debugger:
                return root_node, cwd

            # Create a command argument with the path to the debugger
            # Note that "debugger" is a tag which is only used internally
            debugger_node = ArgsTreeNode(
                "debugger", args=[decorated.get_config('/BUILD/debugger')]
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
