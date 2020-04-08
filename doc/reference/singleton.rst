.. _singleton:

******************
The Dodo singleton
******************

The Dodo singleton class gives Dodo Commands scripts access to the core Dodo Commands functions.

Methods
=======

The is_main function
--------------------

Using ``if Dodo.is_main(__name__)`` instead of the usual ``if __name__ == '__main__'`` allows Dodo Commands to execute your script when its invoked through calling ``dodo``.


.. code-block:: python

    from dodo_commands.framework import Dodo

    if Dodo.is_main(__name__):
        print("Hello world")


The get function
----------------

Calling ``Dodo.get('/ROOT/my/key', 'default-value')`` will retrieve a value
from the project's configuration. Use ``Dodo.get()`` to get direct
access to the entire configuration dictionary.


The parse_args function (--confirm and --echo)
----------------------------------------------

The ``Dodo.parse_args(parser)`` function uses ``parser`` to parse the arguments in ``sys.argv``. It adds an ``--echo`` and ``--confirm`` flag to the command line arguments of your script:

#. the :code:`--echo` flag changes the behaviour of :code:`run` so that it only prints a command line instead of executing the command.

#. the :code:`--confirm` flag changes the behaviour of :code:`run` so that it prints a command line and asks for confirmation before executing the command.

#. if you use the ``--confirm`` flag twice then also nested ``dodo`` calls (i.e. any calls to ``dodo`` that are executed inside the Dodo Command script) will ask for confirmation.

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
                cwd=Dodo.get('/ROOT/src_dir')
            )


The run function
----------------

The ``Dodo.run`` function takes a list of arguments (and a current working directory) and runs them on the command line. It also adds all variables in ``${/ENVIRONMENT/variable_map}`` to the system environment for the duration of running the command.

.. code-block:: python

    if Dodo.is_main(__name__):
        Dodo.run(['echo', 'hello'], cwd='/tmp')


Config arguments
================

Although it's possible to use ``Dodo.get`` directly inside the ``Dodo.run`` invocation, doing this work in the ``_args()`` helper function yields a better separation of concerns:

.. code-block:: python

    def _args():
        Dodo.parser.add_argument('--verbose')
        args.src_dir = Dodo.get('/ROOT/src_dir')
        return Dodo.args

    if Dodo.is_main(__name__):
        args = _args()
        # You can now use args.src_dir

This approach opens up an interesting possibility: if the requested configuration key is absent then we could still ask the user for a value on the command line. This can be achieved through the ``ConfigArg`` helper class:

.. code-block:: python

    from dodo_commands.framework import Dodo, ConfigArg
    from argparse import ArgumentParser

    def _args():
        parser = ArgumentParser()
        parser.add_argument('--verbose')
        return Dodo.parse_args(parser, config_args=[
          '/ROOT/src_dir', 'src_dir', help="Location of the source files"
        ])

The ``ConfigArg`` is constructed with the configuration key, followed by any (keyword) arguments that ``parser.add_argument`` accepts. If the key is found in the configuration, then the corresponding value will be inserted into the return value of ``Dodo.parse_args``. Otherwise, an extra *argument* will be added to the command line syntax. This ensures that the value is either read from the configuration or from the command line.


Using pipes and redirection
===========================

Since pipes and redirection are handled by the shell, you need to explicitly mention the shell executable to use them, e.g.

.. code-block:: python

    if Dodo.is_main(__name__):
        args = _args()
        Dodo.run(['/bin/bash', '-c', 'echo \'Hello world\' > /tmp.out'])


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
