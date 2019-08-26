.. _configuration:

*******************
Configuration files
*******************

After activating a project such as FooBar with :code:`$(dodo activate FooBar)`, the project's configuration file is accessible to any command that you execute.
This chapter explains how to store values in the configuration file and use them in a command script.


Configuration files
===================

A new configuration file is created automatically when the project is first created (e.g. :code:`~/projects/FooBar/dodo_commands/res/config.yaml`). You can print the configuration file with ``dodo print-config``. The configuration file uses the yaml format, with a few extra rules:

1. environment variables (such as ``$PATH``) in values are expanded automatically. Note that unresolved variables of the shape ``$FOO`` are ignored, whereas variables of the shape ``${FOO}`` will result in an error if they are not resolved.

2. values may reference other values in the configuration file:

.. code-block:: yaml

    BUILD:
        nr_of_threads: 2
    FOO:
        bar: ${/BUILD/nr_of_threads}      # value will be the number 2
        ${/BUILD/nr_of_threads}_foo: baz  # key will be the string "2_foo"

3. the following magic values are automatically added: ``${/ROOT/project_name}``, ``${/ROOT/project_dir}``, ``${/ROOT/res_dir}``. Finally the dodo_system_commands directory is automatically added to ``${/ROOT/command_path}``.

4. ``${/ROOT/layers}`` lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in the layer, then values replace values, lists are concatenated, and dictionaries are merged. Layers are found relative to the resources directory that holds all configuration files. However, layers may also be prefixed with an absolute path. Moreover, wildcards are allowed. To list all active layers, use ``dodo which --layers``.

.. code-block:: yaml

    ROOT:
        layers:
            # contents of this file are layered on top of this configuration
            - buildtype.debug.yaml
            # layer with an absolute path
            - ~/.dodo_commands/default_layer.yaml
            # example of using wildcards
            - ~/.dodo_commands/default_layers/*.yaml

Layers can be switched on and off with the ``dodo layer`` command (except for the ones with absolute paths). In the above example, to replace the layer ``buildtype.debug.yaml`` with ``buildtype.release.yaml`` call:

.. code-block:: bash

    dodo layer buildtype release

5. All files in ``{/ROOT/dotenv_files}`` are loaded with ``python-dotenv`` and used in the expansion of environment variables in the Dodo configuration. Note that these values are not added to the environment during the execution of a command script.

Using configuration values in scripts
=====================================

To use a configuration value in your script, call ``Dodo.get_config('/SOME/path/to/the/value')``. By convention, items in the root of the configuration are capitalized. Though you will rarely need to, you can access array elements by index, e.g. ``Dodo.get_config('/SOME/array/3/name')``. Finally, you can specify a fallback value, e.g. ``Dodo.get_config('/ROOT/maybe/some/value', 42)``


How to use layers
=================

The layering mechanism is simple but powerful. As an example, consider placing the settings for different web servers in ``server.develop.yaml``, ``server.staging.yaml`` and ``server.production.yaml``. You can now select a server (staging, for example) with ``dodo layer server staging``. Another common use-case is switching between debug and release builds.

.. note::

    Calling ``dodo layer foo bar`` makes a small change in your configuration file by adding ``foo.bar.yaml`` to the ``${/ROOT/layers}`` node. Make sure that you do not have any unsaved configuration changes before calling this command.

An alternative way to select a layer is using the ``--layer`` option (which you can use more than once per call). For example, ``dodo print-config --layer foo.baz.yaml ROOT`` loads the ``foo.baz.yaml`` layer and then prints the contents of the ``ROOT`` configuration key.

Note that the layers ``foo.bar.yaml`` and ``foo.baz.yaml`` are considered to be mutually exclusive variations of the ``foo`` layer. Therefore, the use of ``--layer foo.baz.yaml`` will nullify any layer such as ``foo.bar.yaml`` in ``${/ROOT/layers}``.


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



Including bits of configuration from packages
=============================================

When you install a package with ``dodo install-commands`` it may contain more than just command scripts. Some packages contain a so-called "drop-in" directory with configuration files and other resources such as Dockerfiles. Since the Dodo Commands philosophy is that you own your local configuration, the way to use these files is through copying them:

.. code-block:: bash

    dodo install-commands --pip dodo_deploy_commands
    # copy drop-in directory to ${/ROOT/res_dir}/drops/dodo_deploy_commands
    dodo drop-in dodo_deploy_commands

The ``dodo drop-in`` command copies the package's "drop-in" directory to ``${/ROOT/res_dir}/drops/<package_name>``. The default location of the ``drop-in`` source directory is in the root of the package. Alternatively, the package root may contain a ``.drop-in`` file that holds the relative path to the actual ``drop-in`` directory.

You can use a copied configuration file by including it as a layer:

.. code-block:: bash

    # enable layer (drop.on.yaml)
    dodo layer drops/dodo_deploy_commands/drop on
    # disable layer (drop.off.yaml)
    dodo layer drops/dodo_deploy_commands/drop off


Preserving the configuration history
====================================

Breaking your local configuration can be serious problem, because it stops all Dodo Commands from working. Therefore, it's advisable to store your local configuration in a local git repository so that you can always restore a previous version. The ``dodo commit-config`` command makes this easy. It initializes a local git repository (if one doesn't exist already) next to your configuration files, and stages and commits all changes to the configuration.


.. _global_config:

The global configuration file
=============================

The location of the global configuration file can be obtained with ``dodo which --global-config``. From the command line, you can set a global configuration value ``foo`` in the ``bar`` section using ``dodo global-config bar.foo somenewvalue``.
