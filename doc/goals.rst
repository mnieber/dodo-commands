*********************************
Goals of the Dodo Commands system
*********************************

The Dodo Commands system supports various goals. The following list skips
some of the details, but gives a general overview. To see a use-case, visit this `page <https://github.com/mnieber/dodo_commands>`_.

Single entry point to run a variety of command scripts
======================================================

If you have a large number of command scripts, it becomes tedious to remember where
they are stored. When you type :code:`dodo foo --bar` then Dodo Commands finds the foo.py script for you and runs it with the --bar option. When you run :code:`dodo help` you will see the list of available commands.

Show what each command script does
==================================

Running :code:`dodo foo --bar --confirm` makes the foo.py script print each command line call that it executes, and ask for confirmation. This allows you to see exactly what the script does. By copy-and-pasting the printed command, you will be able to run it manually.

Give access to the configuration of the current project
=======================================================

Dodo Commands try to replace long command line calls with short aliases that fetch their arguments from the configuration file of the currently active project. Running :code:`dodo foo --bar` gives the ``foo.py`` script access to the current project's configuration.

Run commands in a docker container
==================================

You can make certain commands execute inside a docker container. Dodo Commands will read the project configuration to find out which volume mappings and environment variables it must create inside the container.

Install dependencies automatically
==================================

By specifying the dependencies of a command script in a :code:`<script-name>.meta` file, missing Python packages are automatically installed into the virtualenv of the Dodo Commands project.

Auto-completion
===============

When using bash, Dodo Commands provides auto-completion of the command names and their arguments (all argument parsing is done with the argparse package).
