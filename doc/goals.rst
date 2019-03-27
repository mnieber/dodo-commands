*********************************
Goals of the Dodo Commands system
*********************************

The main goal is to associate a set of short commands with each project to automate frequent tasks. The following list gives a general overview of how this achieved. We also encourage you to try the tutorial on this `page <https://github.com/mnieber/dodo_commands>`_.

Provide a per-project environment
=================================

Each Dodo Commands project contains a specific set of commands and configuration values. It's also possible to install default commands that will be available in any project.

Single entry point to run a variety of command scripts
======================================================

Dodo Commands finds command scripts for you in the project's search path, so there is no need to remember where they are located. This means that commands work from any current working directory. Running :code:`dodo help` shows the list of available commands.

Give access to the configuration of the current project
=======================================================

Dodo Commands fetches arguments from the current project's configuration file. However, arguments not found in the configuration file can still be obtained from the command line.

Flexible configurations
=======================

Configuration files can be layered, and layers can be switched on or off, giving you a lot of flexibility. Just like excel sheets, configuration files may contain cross-references. The power of Dodo Commands is mostly in the configuration file.

Show what each command script does
==================================

In some cases you don't want to run a script blindly. Running :code:`dodo foo --bar --confirm` makes the foo.py script print each command line call that it executes, and ask for confirmation. This allows you to see exactly what the script does.

Share commands easily, while allowing customization
===================================================

You can synchronize your local project configuration with a shared one. This works by cherry-picking the parts you need. New colleagues can initialize their project by boot-strapping from the shared configuration.

Run commands in a docker container
==================================

You can tell Dodo Commands to prefix particular commands with a Docker invocation. The appropriate volume mappings, environment variables, etc come from the configuration file.

Install dependencies automatically
==================================

By specifying the dependencies of a command script in a :code:`<script-name>.meta` file, missing Python packages can be automatically installed into the virtualenv of the current Dodo Commands project.
