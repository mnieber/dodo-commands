***********************************
Globally used directories and files
***********************************

The following files are accessible by all Dodo Commands environments:

global configuration file
-------------------------

Value: ``~/.dodo_commands/config``. Ini file that contains the global configuration settings

global commands directory
-------------------------

Value: ``~/.dodo_commands/commands``. The directory that contains all globally installed command packages

default project directory
-------------------------

Value: ``~/.dodo_commands/default_project``. The directory that contains the project files for the default environment.

default commands directory
--------------------------

Value: ``~/.dodo_commands/default_project/commands``. The directory that contains the default command packages (these are symlinks to packages in the global commands directory)

global bin directory: ~/.dodo_commands/bin
------------------------------------------

A directory that contains an executable per environment (e.g. dodo-foo) for using that environment directly. Calling ``dodo-<name> which`` will always return ``<name>``.