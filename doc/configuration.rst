*******************
Configuration files
*******************

Once you have activated a project such as FooBar with :code:`$(dodo activate FooBar)`, you will continue to work with that project's configuration file and set of command scripts.

Configuration files
===================

A new configuration file is created automatically when the project is first created (e.g. :code:`~/projects/FooBar/dodo_commands/res/config.yaml`). The configuration file uses the yaml format, with a few extra rules:

1. environment variables in values are expanded automatically

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

4. ${/ROOT/layers} lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in a layer configuration, then values replace values, lists are concatenated, and dictionaries are merged. The ROOT/layer_dir value can be used to specify the sub-directory where layer configuration files are searched:

.. code-block:: yaml

    ROOT:
        layer_dir: layers
        layers:
            - buildtype.debug.yaml  # contents of this file are layered on top of this configuration

5. the following magic values are automatically added: ${/ROOT/project_name},  ${/ROOT/project_dir} and ${/ROOT/res_dir}.

Using the configuration
=======================

As explained in the :ref:`commands` section, commands can obtain configuration values by calling :code:`self.get_config(<key>)`.
