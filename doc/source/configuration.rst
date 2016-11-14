*******************
Configuration files
*******************

Once you have activated a project such as FooBar with :code:`$(dodo-activate FooBar)`, you will continue to work with that project's configuration file and set of command scripts.

Configuration files
===================

In the most common case, a new configuration file is created automatically when the project is first created (e.g. :code:`~/projects/FooBar/dodo_commands/config.yaml`). The configuration file uses the yaml format, with a few extra rules:

1. environment variables in values are expanded automatically

2. special "dodo environment" variables refer to other values in the configuration file:

.. code-block:: yaml

    BUILD:
        nr_of_threads_EVAL: 2
    FOO:
        bar: ${/BUILD/nr_of_threads}  # value will be the number 2

3. if a configuration key ends in _EVAL, then its associated value is evaluated in Python and stored as a string. If the associated value is a list or dictionary, then every value in that list or dictionary is evaluated (but not recursively). Use with caution! For example:

.. code-block:: yaml

    BUILD:
        nr_of_threads_EVAL: (2 + 4)  # evaluates to the string "6"
    FOO:
        bar_EVAL:
        - (1 + 2)  # evaluates to "3"
        - (3 + 4)  # evaluates to "7"
        foobar: ${/BUILD/nr_of_threads_EVAL}  # value will be "6"

4. ${/ROOT/layers} lists additional yaml files that are layered on top of the root configuration file. If a key exists both in the root configuration and in a layer configuration, then values replace values, lists are concatenated, and dictionaries are merged. The ROOT/layer_dir value can be used to specify the sub-folder where layer configuration files are searched:

.. code-block:: yaml

    ROOT:
        layer_folder: layers
        layers:
            - buildtype.debug.yaml  # contents of this file are layered on top of this configuration

5. the following magic values are automatically added: ${/ROOT/project_name}, ${/ROOT/project_dir} and ${/ROOT/system_dir} (the latter points to the Dodo commands installation folder)

Using the configuration
=======================

As explained in the :ref:`commands` section, commands can obtain configuration values by calling :code:`self.get_config(<key>)`.

Preset configuration files
==========================

It's often useful to share a configuration file between different people. At the same time, different people will want to tweak their configuration in different ways. This is resolved as follows:

#. the shared configuration file is stored in a git repository, under the path :code:`<projectname>/config.yaml`. For the example of the FooBar project, let's assume we stored FooBar/config.yaml in the https://github.com/foo/myprojects.git repository.

#. this git repository is cloned locally using: :code:`dodo-install-defaults --projects https://github.com/foo/myprojects.git`.

#. when the FooBar project is created using :code:`$(dodo-activate FooBar --create)`, the shared configuration file is found and copied to the project folder. The users can tweak this copy however they want.

#. (provided you installed the default_dodo_commands with dodo-install-defaults) after git pulling the latest version of the original configuration file, you can call :code:`dodo diff config.yaml` to show the difference between the copied and original config.yaml, and manually synchronize the two files. It's a good practice to use the value ${/ROOT/version} to track whether the copied configuration is up-to-date or not.
