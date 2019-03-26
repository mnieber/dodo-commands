*********************************
Goals of the Dodo Commands system
*********************************

The main goal is to associate a set of short commands with each project to automate frequent tasks. The following list gives a general overview of how this achieved. We also encourage you to try the tutorial on this `page <https://github.com/mnieber/dodo_commands>`_.

Provide a per-project environment
=================================

Each Dodo Commands project contains a specific set of commands and configuration values. It's possible to install default commands that will be available in any project.

Single entry point to run a variety of command scripts
======================================================

Since Dodo Commands can find command scripts for you in the project's search path, there is no need to remember where they are located. This means that commands work from any current working directory. Running :code:`dodo help` shows the list of available commands.

Give access to the configuration of the current project
=======================================================

Dodo Commands are usually short because arguments are fetched from the current project's configuration file. Configuration files can be layered, and layers can be switched on or off, giving you a lot of flexibility. Just like excel sheets, configuration files may contain cross-references. The power of Dodo Commands is mostly in the configuration file.

Flexibly switch between configuration and command line arguments
================================================================

Dodo Commands supports a model where arguments not found in the configuration file are obtained from the command line.

Show what each command script does
==================================

In some cases you don't want to run a script blindly. Running :code:`dodo foo --bar --confirm` makes the foo.py script print each command line call that it executes, and ask for confirmation. This allows you to see exactly what the script does.

Share commands easily, while allowing customization
===================================================

*You* control your local project configuration, but it's easy to synchronize with a shared configuration by cherry-picking the parts you need. New colleagues can initialize their project by boot-strapping from the shared configuration.

Run commands in a docker container
==================================

You can tell Dodo Commands to prefix particular commands with a docker invocation. Dodo Commands will read the project configuration to find out which volume mappings and environment variables it must create inside the container before running your command.

Install dependencies automatically
==================================

By specifying the dependencies of a command script in a :code:`<script-name>.meta` file, missing Python packages can be automatically installed into the virtualenv of the current Dodo Commands project.
