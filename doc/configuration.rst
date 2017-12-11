*******************
Configuration files
*******************

Activating a project such as FooBar with :code:`$(dodo activate FooBar)` implies that this project's configuration file is used for any command that you execute. This chapter explains how to store values in the configuration file and use them in a command script.


Configuration files
===================

A new configuration file is created automatically when the project is first created (e.g. :code:`~/projects/FooBar/dodo_commands/res/config.yaml`). The configuration file uses the yaml format, with a few extra rules:

1. environment variables (such as ``$PATH``) in values are expanded automatically

2. special "dodo environment" variables refer to other values in the configuration file:

.. code-block:: yaml

    BUILD:
        nr_of_threads: 2
    FOO:
        bar: ${/BUILD/nr_of_threads}      # value will be the number 2
        ${/BUILD/nr_of_threads}_foo: bar  # key will be the string "2_foo"

3. if a configuration key ends in _EVAL, then its associated value is evaluated in Python and stored as a string. If the associated value is a list or dictionary, then every value in that list or dictionary is evaluated (but not recursively). Use with caution! For example:

.. code-block:: yaml

    BUILD:
        nr_of_threads_EVAL: (2 + 4)  # evaluates to the string "6"
    FOO:
        bar_EVAL:
        - (1 + 2)  # evaluates to "3"
        - (3 + 4)  # evaluates to "7"
        foobar: ${/BUILD/nr_of_threads_EVAL}  # value will be "6"

4. ``${/ROOT/layers}`` lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in a layer configuration, then values replace values, lists are concatenated, and dictionaries are merged. The ``${/ROOT/layer_dir}`` value can be used to specify the sub-directory where layer configuration files are searched. However, layers may also be prefixed with an absolute path. Finally, wildcards are allowed.

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


5. the following magic values are automatically added: ``${/ROOT/project_name}``, ``${/ROOT/project_dir}``, ``${/ROOT/res_dir}``. Finally the system_commands directory is automatically added to ``${/ROOT/command_path}``.

Using the configuration
=======================

As explained in the :ref:`commands` section, commands can obtain configuration values by calling :code:`self.get_config(<key>)`.
