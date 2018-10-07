*********************************
Goals of the Dodo Commands system
*********************************

The Dodo Commands system supports various goals, the main one being: associate a set of short commands with each project to automate frequent tasks. The following list skips some of the details, but gives a general overview. To see a use-case, visit this `page <https://github.com/mnieber/dodo_commands>`_.

Provide a per-project environment
=================================

Dodo Commands run in the context of a project. When you switch to a project, you will have a specific set of commands and configuration values available to you. At the same time, it's possible to install default commands that will be available in any project.

Single entry point to run a variety of command scripts
======================================================

If you have a large number of command scripts, it becomes tedious to remember where
they are stored. Running :code:`dodo foo --bar` let's Dodo Commands find the foo.py script for you in the current project's search path. This works from any current working directory. When you run :code:`dodo help` you will see the list of available commands.

Give access to the configuration of the current project
=======================================================

Dodo Commands try to replace long command line calls with short aliases that fetch their arguments from the current project's configuration file. Configuration files can be layered, and switched on or off, giving you a lot of flexibility. Just like excel sheets, configuration files may contain cross-references. The power of Dodo Commands is mostly in the configuration file.

Show what each command script does
==================================

In some cases you don't want to run a script blindly. Running :code:`dodo foo --bar --confirm` makes the foo.py script print each command line call that it executes, and ask for confirmation. This allows you to see exactly what the script does. By copy-and-pasting the printed command, you will be able to run it manually.

Share commands easily, while allowing customization
===================================================

*You* control your local project configuration, but it's easy to synchronize with a shared configuration by cherry-picking the parts you need. New colleagues can initialize their project by boot-strapping from the shared configuration.

Run commands in a docker container
==================================

You can make certain commands execute inside a chosen docker container. Dodo Commands will read the project configuration to find out which volume mappings and environment variables it must create inside the container before running your command.

Install dependencies automatically
==================================

By specifying the dependencies of a command script in a :code:`<script-name>.meta` file, missing Python packages can be automatically installed into the virtualenv of the current Dodo Commands project.

Auto-completion
===============

When using bash, Dodo Commands provides auto-completion of the command names and their arguments (all argument parsing is done with the argparse package).
