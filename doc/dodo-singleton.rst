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

Calling ``Dodo.get_config('/ROOT/my/key', 'default-value')`` will retrieve a value from the project's :ref:`configuration`. Use ``Dodo.get_config()`` to get direct access to the entire configuration dictionary.


The parse_args function (--confirm and --echo)
==============================================

The ``Dodo.parse_args(parser)`` function uses ``parser`` to parse the arguments in ``sys.argv``. It adds an ``--echo`` and ``--confirm`` flag to the command line arguments of your script:

#. the :code:`--echo` flag changes the behaviour of :code:`run` so that it only prints a command line instead of executing the command.

#. the :code:`--confirm` flag changes the behaviour of :code:`run` so that it prints a command line and asks for confirmation before executing the command.

Note that although the ``--echo`` and ``--confirm`` flags are included in the return value of ``Dodo.parse_args``, there is no need to pass them to ``Dodo.run``. This is because the ``Dodo`` singleton also stores them internally.

If you call ``Dodo.parse_args`` then you should do so before any calls to ``Dodo.run`` so that ``--echo`` and ``--confirm`` can take effect:

.. code-block:: python

    from dodo_commands.framework import Dodo
    from argparse import ArgumentParser

    def _args():
        parser = ArgumentParser()
        parser.add_argument('--verbose')
        return Dodo.parse_args(parser)

    if Dodo.is_main(__name__):
        args = _args()

        if args.verbose:
            Dodo.run(
                ['echo', 'hello world'],
                cwd=Dodo.get_config('/ROOT/src_dir')
            )


Config arguments
================

Although it's possible to use ``Dodo.get_config`` directly inside the ``Dodo.run`` invocation, doing this work in the ``_args()`` helper function yields a better separation of concerns:

.. code-block:: python

    def _args():
        parser = ArgumentParser()
        parser.add_argument('--verbose')
        args = Dodo.parse_args(parser)
        args.src_dir = Dodo.get_config('/ROOT/src_dir')
        return args

    if Dodo.is_main(__name__):
        args = _args()
        # You can now use args.src_dir

This approach opens up an interesting possibility: if the requested configuration key is absent then we could still ask the user for a value on the command line. This can be achieved through the ``ConfigArg`` helper class:

    from dodo_commands.framework import Dodo, ConfigArg
    from argparse import ArgumentParser

    def _args():
        parser = ArgumentParser()
        parser.add_argument('--verbose')
        return Dodo.parse_args(parser, config_args=[
            '/ROOT/src_dir', 'src_dir', help="Location of the source files"
        ])

The ``ConfigArg`` is constructed with the configuration key, followed by any (keyword) arguments that ``parser.add_argument`` accepts. If the key is found in the configuration, then the corresponding value will be inserted into the return value of ``Dodo.parse_args``. Otherwise, an extra *argument* will be added to the command line syntax. This ensures that the value is either read from the configuration or from the command line.


The run function
===================

The ``Dodo.run`` function takes a list of arguments (and a current working directory) and runs them on the command line. It also adds all variables in ``${/ENVIRONMENT/variable_map}`` to the system environment for the duration of running the command.

.. code-block:: python

    if Dodo.is_main(__name__):
        Dodo.run(['echo', 'hello'], cwd='/tmp')


Marking a script as unsafe
==========================

Since command scripts are written in Python, the script can in principle perform any operation without explicitly asking your permission. In other words, it may choose to ignore the ``--confirm`` and ``--echo`` options. This sitation should of course be avoided. However, if a Command script does not completely honor the ``--confirm`` and ``--echo`` flags, it should pass ``safe=False`` when it calls ``Dodo.is_main``, as shown in the example below. Unsafe commands will not run with the --echo flag, and will pause with a warning when run with the --confirm flag.

.. code-block:: python

    if Dodo.is_main(__name__, safe=False): # NOTE: setting the _safe flag here
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
