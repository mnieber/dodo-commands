.. _decorators:

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

Because the ``DodoCommand`` class implements :code:`add_arguments` and :code:`handle`, subclasses of ``DodoCommand`` must now implement :code:`add_arguments_imp` and :code:`handle_imp` instead.

Note that since command scripts are written in Python, it's not guaranteed that all operations are confirmed or echoed to the screen. Command scripts that do not completely honor the ``--confirm`` and ``--echo`` flags should be marked with ``safe = False``, as shown in the example below. Unsafe commands will not run with the --echo flag, and will pause with a warning when run with the --confirm flag.

.. code-block:: python

    class Command(DodoCommand):  # noqa
        safe = False

        # rest of the command goes here...


Decorators
==========

A Decorator is a class that alters the workings of a DodoCommand class. It can extend or modify the arguments that are passed to ``DodoCommand.handle``. The decorator should be placed in a ``decorators`` directory inside a commands directory. This is illustrated by the following example:

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

        def modify_args(self, decorated, args, cwd):  # noqa
            if not decorated.opt_use_debugger:
                return args, cwd

            new_args = [decorated.get_config('/BUILD/debugger')] + args
            return new_args, cwd

Note that not all decorators are compatible with all commands. For example, only some commands can be run inside a debugger. Therefore, for each decorator you should list in the configuration which commands are decorated. When listing the commands, wildcards are allowed, and you can exclude commands by prefixing them with an exclamation mark:

.. code-block:: yaml

    ROOT:
      decorators:
        # Use a wildcard to decorate all commands, but exclude the foo command
        debugger: ['*', '!foo']
        # cmake and runserver can be run inside docker
        docker: ['cmake', 'runserver']

The docker decorator
====================

If the "docker" decorator is used and the ``${/DOCKER/enabled}`` configuration value is true, then all command lines will be prefixed with ``/usr/bin/docker run`` and related docker arguments:

#. each key-value pair in ``$(/DOCKER/volume_map}`` will be added as a docker volume (where 'key' in the host maps to 'value' in the docker container)

#. each item in ``$(/DOCKER/volume_list}`` will be added as a docker volume (where 'item' in the host maps to 'item' in the docker container)

#. each item in ``$(/DOCKER/volumes_from_list}`` will be added as a docker "volumes_from" argument

#. each item in ``$(/DOCKER/link_list}`` will be added as a docker "link" argument

#. each environment variable listed in ``$(/DOCKER/variable_list}`` or ``$(/DOCKER/variable_map}`` will be added as an environment variable in the docker container. Variables in ``variable_list`` have the same name in the host and in the container.

#. each key-value pair in ``$(/ENVIRONMENT/variable_map}`` will be added as an environment variable in the docker container.

#. arguments in ``${/DOCKER/extra_options}`` are passed as extra options to the docker command line call.

#. the ``--rm`` flag is added by default. The ``-i`` and ``-t`` flags are added unless you pass the ``--non-interactive`` flag.
