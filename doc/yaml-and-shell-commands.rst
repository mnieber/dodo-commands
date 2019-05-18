.. _yaml_and_shell_commands:

***********************
YAML and shell commands
***********************

-------------------
YAML command syntax
-------------------

Instead of using Python, you can also create a Dodo command by writing a YAML file. This file should have ``dodo.`` as a prefix, e.g. ``dodo.my-commands.yaml``. Each key in the root of the YAML file corresponds to a command. The command node can have the following items:

- a ``_description`` that is printed when the ``--help`` option is used
- a ``_args`` list with command line arguments for the command. You can access these arguments in the command steps via the ``${/_ARGS}`` dictionary.
- one or more command steps. Each step is a name-value pair. The name is ignored, but you can use it to document the step. The value is a dictionary with ``args`` and a ``cwd``.

For example:

.. code-block:: yaml

    clean-images:
      _description: "Remove images from the foo directory"
      first print the image filenames:
        args: ls *.jpg
        cwd: /tmp/foo/
      then remove them:
        args: rm *.jpg
        cwd: /tmp/foo/
    say-hello:
      _args: ['name']
      main:
        args: ['echo', 'hello', '${/_ARGS/name}']

--------------------
Shell command syntax
--------------------

A shell command file should have ``dodo.`` as a prefix, e.g. ``dodo.my-command.sh``. For the rest, the command file should be a normal shell script.