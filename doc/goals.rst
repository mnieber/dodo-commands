*********************************
Goals of the Dodo Commands system
*********************************

The Dodo Commands system supports various goals. The following list skips
some of the details, but gives a general overview:

Single entry point to run a variety of command scripts
======================================================

If you have a large number of command scripts, it becomes tedious to remember where
they are stored. When you type :code:`dodo foo --bar`, then Dodo Commands will find the foo.py script for you and run it with the --bar option. When you run :code:`dodo help` you will see the list of available commands.

Show what each command script does
==================================

When you run :code:`dodo foo --bar --confirm` then the foo.py script will print each command line call before it is executed, and ask for confirmation. This allows you to see exactly what the script does. By copy-and-pasting the printed command, you will be able to run it manually.

Give access to the configuration of the current project
=======================================================

Script code and configuration values should remain separate. When you run :code:`dodo foo --bar` then the foo.py script will have access to the configuration values of the currently
active project.

Run commands in a docker container
==================================

If you enable docker support, and if the command is runnable in docker, then the command will execute inside a docker container. Dodo Commands will read the project configuration to find out which volume mappings and environment variables it must create inside the container.

Install dependencies automatically
==================================

By specifying the dependencies of a command script in a :code:`<script-name>.meta` file, missing Python packages are automatically installed into the virtualenv of the Dodo Commands project.

Auto-completion
===============

Dodo Commands provides auto-completion of the command names and their arguments (all argument parsing is done with the argparse package).
