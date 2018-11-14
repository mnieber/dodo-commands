.. _singleton:

******************
The Dodo singleton
******************

This chapter describes the functions offered by the Dodo singleton class. You can use these functions in any Dodo Command script.


The is_main function
====================

Using ``if Dodo.is_main(__name__)`` instead of the usual ``if __name__ == '__main__'`` allows Dodo Commands to execute your script when its invoked through calling ``dodo``.


.. code-block:: python

    from dodo_commands.framework import Dodo

    if Dodo.is_main(__name__):
        print("Hello world")


The get_config function
=======================

Calling ``Dodo.get_config('/ROOT/my/key', 'default-value')`` will retrieve a value from the project's :ref:`configuration`. Use ``Dodo.config`` to get direct access to the configuration dictionary.


The run function
===================

The ``Dodo.run`` function takes a list of arguments (and a current working directory) and runs them on the command line. It also adds all variables in ``${/ENVIRONMENT/variable_map}`` to the system environment for the duration of running the command.

.. code-block:: python

    if Dodo.is_main(__name__):
        # Note that you must call Dodo.parse_args before calling Dodo.run,
        # or an exception will be raised
        parser = ArgumentParser()
        parser.add_argument(
            '--verbose',
            action="store_true",
        )
        args = Dodo.parse_args(parser)

        # say hello
        if args.verbose:
            Dodo.run(['echo', 'hello'], cwd='/tmp')


The --confirm and --echo flags
==============================

The ``Dodo.parse_args(parser)`` function adds an ``--echo`` and ``--confirm`` flag the to command line arguments of your script. These flags control what happens in the ``Dodo.run`` function:

#. the :code:`--echo` flag changes the behaviour of :code:`run` so that it only prints a command line instead of executing the command.

#. the :code:`--confirm` flag changes the behaviour of :code:`run` so that it prints a command line and asks for confirmation before executing the command.


Marking a script as unsafe
==========================

Since command scripts are written in Python, the script can in principle perform any operation without explicitly asking your permission. In other words, it may choose to ignore the ``--confirm`` and ``--echo`` options. This sitation should of course be avoided. However, if a Command script does not completely honor the ``--confirm`` and ``--echo`` flags, it should pass ``safe=False`` when it calls ``Dodo.is_main``, as shown in the example below. Unsafe commands will not run with the --echo flag, and will pause with a warning when run with the --confirm flag.

.. code-block:: python

    if Dodo.is_main(__name__, safe=False): # NOTE: setting the _safe flag here
        parser = ArgumentParser()
        args = Dodo.parse_args(parser)

        # Do destructive things without asking permission. Having this call
        # is the reason we used safe=False to mark the script as unsafe.
        # Running the script with ``--echo`` is not possible, because that would
        # lead to unpleasant surprises. Running with ``--confirm`` will inform
        # you that unpleasant surprises can be expected if you continue.
        os.unlink('/tmp/foo.text')

        # Delete the /tmp directory. Since this time we are using Dodo.run,
        # the user can use the --confirm flag to inspect and cancel it.
        # This makes this call *relatively* safe, but if you blindly run this script (without
        # using ``--confirm``) you may still be unpleasantly surprised.
        Dodo.run(['rm', '-rf', '/tmp'])
