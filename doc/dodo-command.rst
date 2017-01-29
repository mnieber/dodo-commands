.. _decorators:

*********************
The DodoCommand class
*********************

The :code:`BaseCommand` class is pretty simple: it offers access to the project configuration
and a command line parser. The :code:`DodoCommand` class extends BaseCommand with advanced features.


The runcmd function, and --confirm and --echo flags
===================================================

The :code:`DodoCommand` class adds a helper function :code:`runcmd` and two additional flags to each command:

#. the runcmd class takes a list of arguments and runs them on the command line. Moreover, it loads any variables in ${/ENVIRONMENT/variable_map} from the configuration and adds them to the system environment.

#. the :code:`--echo` flag changes the behaviour of :code:`runcmd` so that it only prints the arguments instead of executing them.

#. the :code:`--confirm` flag changes the behaviour of :code:`runcmd` so that it asks for confirmation before executing a command line.

Because the :code:`DodoCommand` class implements :code:`add_arguments` and :code:`handle`, subclasses must now implement :code:`add_arguments_imp` and :code:`handle_imp` instead.

Decorators
==========

A Decorator is a class that alters the workings of a DodoCommand class:

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

The docker decorator
====================

If the "docker" decorator is used and the ${/DOCKER/enabled} configuration value is true, then all command lines will be prefixed with :code:`/usr/bin/docker run` and related docker arguments:

#. each key-value pair in $(/DOCKER/volume_map} will be added as a docker volume (where 'key' in the host maps to 'value' in the docker container)

#. each item in $(/DOCKER/volume_list} will be added as a docker volume (where 'item' in the host maps to 'item' in the docker container)

#. each environment variable listed in $(/DOCKER/variable_list} or $(/DOCKER/variable_map} will be added as an environment variable in the docker container.

#. each key-value pair in $(/ENVIRONMENT/variable_map} will be added as an environment variable in the docker container.

#. arguments in ${/DOCKER/extra_options} are passed as extra options to the docker command line call.

#. the '--rm' flag is added be default. The '-i' and '-t' flags are added unless you pass the --non-interactive flag.