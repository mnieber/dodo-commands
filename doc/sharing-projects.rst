.. _sharing_projects:

****************
Sharing projects
****************

Sharing projects
================

If your working environment uses scripts and configuration files, and someone wants to join the work, then it makes
sense to share your working environment with them. At the same time, you want your working environment to be independent,
so that you can arrange it to your preferences.

Sharing project files
=====================

With project files we mean all files that you keep in the :code:`~/projects/<project name>/dodo_commands` directory, such as:

- the configuration files such as config.yaml
- configuration layer files (that can be superimposed on config.yaml)
- docker files

To share these files, but still allow everyone to make local changes:

#. the shared project is stored in a directory - named after the project - inside the root of a git repository (for example: https://github.com/foo/myprojects.git).

#. this git repository is cloned locally using: :code:`dodo-install-defaults --git --projects https://github.com/foo/myprojects.git`. The cloned files are stored in ~/dodo_commands/defaults/projects/myprojects.

#. when the FooBar project is created using :code:`$(dodo-activate FooBar --create)`, all project files are copied from the cloned repository into the local project directory. The users can tweak this copy however they want.

#. (provided you installed the standard_commands with dodo-install-defaults) after git pulling the latest version of the shared project repository (myprojects.git), you can call :code:`dodo diff .` to show the difference between the copied and original project, and manually synchronize the two directories.

#. To synchronize only config.yaml, call :code:`dodo diff config.yaml`. It's a good practice to use the value ${/ROOT/version} to track whether the copied configuration is up-to-date or not.
