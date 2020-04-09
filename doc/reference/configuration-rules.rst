*******************
Configuration rules
*******************

The configuration file uses the yaml format, with a few extra rules:

1. environment variables (such as ``$PATH``) in values are expanded automatically. Note that unresolved variables of the shape ``$FOO`` are ignored, whereas variables of the shape ``${FOO}`` will result in an error if they are not resolved.

2. values may reference other values in the configuration file:

.. code-block:: yaml

    BUILD:
        nr_of_threads: 2
    FOO:
        bar: ${/BUILD/nr_of_threads}      # value will be the number 2
        ${/BUILD/nr_of_threads}_foo: baz  # key will be the string "2_foo"

3. the following magic values are automatically added: ``${/ROOT/project_name}``, ``${/ROOT/project_dir}``, ``${/ROOT/res_dir}``. Finally the dodo_system_commands directory is automatically added to ``${/ROOT/command_path}``.

4. ``${/ROOT/LAYERS}`` lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in the layer, then values replace values, lists are concatenated, and dictionaries are merged. Layers are found relative to the resources directory that holds all configuration files. However, layers may also be prefixed with an absolute path. Moreover, wildcards are allowed. To list all active layers, use ``dodo which --layers``.

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
