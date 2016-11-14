.. _decorators:

**********
Decorators
**********

The Decorator class
===================

A Decorator is a class that alters the workings of a BaseCommand class:
- it can add extra arguments to the command
- it can modify the arguments that are passed to the DodoCommand

The decorator should be placed in a :code:`decorators` directory inside a commands directory.
This is illustrated by the following example:

.. code-block:: python

    # file my_commands/decorators/debugger.py

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

        def modify_args(self, decorated, args, cwd):  # noqa
            if not decorated.opt_use_debugger:
                return args, cwd

            new_args = [decorated.get_config('/BUILD/debugger')] + args
            return new_args, cwd

Classes that want to use the Decorator can declare them in the :code:`decorators` member:

.. code-block:: python

    class Command(DodoCommand):  # noqa
        decorators = [
            "debugger",
        ]

        # rest of the command goes here...

