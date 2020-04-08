********************
The dodo entry point
********************

The ``dodo`` command runs a Dodo Commands script.

dodo --layer=<name> --trace --traceback
=======================================

--layer=<name>
------------------

Adds <name> as a layer to the configuration.

.. note::

  The layers ``foo.bar.yaml`` and ``foo.baz.yaml`` are considered to be mutually exclusive variations of the ``foo`` layer. Therefore, the use of ``--layer foo.baz.yaml`` will nullify any layer such as ``foo.bar.yaml`` in ``${/ROOT/layers}``.

--trace
-------

Instead of running the command, prints an array that contains
the final form (after interpretation) of all the arguments

--traceback
-----------

Instead of writing a short error when a command fails, writes the full stacktrace.

