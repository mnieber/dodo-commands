.. _commands:

********
Commands
********

Dodo Commands has an aliasing system to help you to keep command lines short.


Command aliases
===============

You can add aliases for any dodo command in the ``aliases`` section of :ref:`global_config`, e.g.

.. code-block:: ini

    [alias]
    wh = which
    whpp = which --projects

You can also add aliases in ``${/ROOT/aliases}``.

.. code-block:: yaml

    ROOT:
        aliases:
            pc-foo: print-config --layer foo.bar.yaml


Layer aliases
=============

You can add aliases for any layer in ``${/ROOT/layer_aliases}``, e.g.

.. code-block:: yaml

    ROOT:
        layer_aliases:
            react: server.react.yaml

This offers a convient shortcut for the ``--layer`` argument.
Instead of writing ``dodo --layer server.react.yaml foo`` you can run ``dodo react.foo``. See the section below on Inferred Commands on how to make this even shorter.


Inferred Commands
=================

In case you are always using a command in combination with a specific layer, then you can add it to the inferred commands of that layer:

.. code-block:: yaml

    # Root node in server.react.yaml
    ROOT:
        inferred_commands: ['foo']

Now, when you run ``dodo foo``, then Dodo Commands will detect that the ``server.react.yaml`` layer has ``foo`` as an inferred command, and it will add ``--layer server.react.yaml`` to the command line. In other words, the result is that ``dodo foo`` becomes a shortcut for ``dodo react.foo``. Note that if there are two layers that have ``foo`` as an inferred command, then Dodo Commands will report an error.


Using --trace to inspect the effect of aliases
==============================================

When you pass the ``--trace`` argument in the call to ``dodo`` then Dodo Commands will print the arguments of the fully expanded call and then terminate immediately. This can be used to find out which layers and commands are really run when aliases are used.
