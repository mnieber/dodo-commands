.. _configuration:

*******************
Configuration files
*******************

After activating a project such as FooBar with :code:`$(dodo activate FooBar)`, the project's configuration file is accessible to any command that you execute.
This chapter explains how to store values in the configuration file and use them in a command script.


Configuration files
===================

A new configuration file is created automatically when the project is first created (e.g. :code:`~/projects/FooBar/dodo_commands/res/config.yaml`). You can print the configuration file with ``dodo print-config``. The configuration file uses the yaml format, with a few extra rules:

1. environment variables (such as ``$PATH``) in values are expanded automatically.

2. values may reference other values in the configuration file:

.. code-block:: yaml

    BUILD:
        nr_of_threads: 2
    FOO:
        bar: ${/BUILD/nr_of_threads}      # value will be the number 2
        ${/BUILD/nr_of_threads}_foo: baz  # key will be the string "2_foo"

3. the following magic values are automatically added: ``${/ROOT/project_name}``, ``${/ROOT/project_dir}``, ``${/ROOT/res_dir}``. Finally the dodo_system_commands directory is automatically added to ``${/ROOT/command_path}``.

4. ``${/ROOT/layers}`` lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in the layer, then values replace values, lists are concatenated, and dictionaries are merged. The ``${/ROOT/layer_dir}`` value can be used to specify the sub-directory where layer configuration files are searched. However, layers may also be prefixed with an absolute path. Finally, wildcards are allowed.

.. code-block:: yaml

    ROOT:
        layer_dir: layers
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

If you want to keep your layers in a separate directory, use the ``${ROOT/layer_dir}`` setting. To list all active layers, use ``dodo which --layers``.


Including bits of configuration from packages
=============================================

When you install a package with ``dodo install-default-commands`` it may contain more than just command scripts. Some packages contain a so-called "drop-in" directory with configuration files and other resources such as Dockerfiles. Since the Dodo Commands philosophy is that you own your local configuration, the way to use these files is through copying them:

.. code-block:: bash

    dodo install-default-commands --pip dodo_deploy_commands
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
